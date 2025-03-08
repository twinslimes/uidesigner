import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="UI to Prompt Designer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing elements
if 'elements' not in st.session_state:
    st.session_state.elements = []
    st.session_state.canvas_height = 600
    st.session_state.canvas_width = 1000

# Custom CSS to make the app full-screen and remove padding
st.markdown("""
    <style>
        .main > div {
            padding-top: 0rem;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0rem;
        }
        .element-container {
            margin: 0 !important;
        }
        .canvas {
            width: 100%;
            height: 600px;
            border: 2px dashed #ccc;
            position: relative;
            background-color: #f5f5f5;
            overflow: hidden;
        }
        .ui-element {
            position: absolute;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for tools
with st.sidebar:
    st.title("🎨 UI Elements")
    
    # Tool selection
    selected_tool = st.radio(
        "Select Tool",
        ["Window", "Sidebar", "Button", "Text Input", "Dropdown", "Select Box"]
    )
    
    # Tool properties
    st.subheader("Properties")
    if selected_tool:
        col1, col2 = st.columns(2)
        with col1:
            x_pos = st.number_input("X Position", 0, st.session_state.canvas_width, 100)
        with col2:
            y_pos = st.number_input("Y Position", 0, st.session_state.canvas_height, 100)
            
        width = st.slider("Width", 50, 800, 200)
        height = st.slider("Height", 50, 600, 200)
        
        if selected_tool in ["Button", "Text Input"]:
            text = st.text_input("Label", "New " + selected_tool)
        
        if selected_tool == "Dropdown":
            options = st.text_area("Options (one per line)", "Option 1\nOption 2\nOption 3")
        
        # Add element button
        if st.button("Add Element"):
            new_element = {
                "id": f"element-{len(st.session_state.elements)}",
                "type": selected_tool,
                "x": x_pos,
                "y": y_pos,
                "width": width,
                "height": height,
                "text": text if 'text' in locals() else "",
                "options": options.split('\n') if 'options' in locals() else []
            }
            st.session_state.elements.append(new_element)
            st.rerun()

    # Clear canvas button
    if st.button("Clear Canvas"):
        st.session_state.elements = []
        st.rerun()

    # Export button
    if st.button("Export Design"):
        export_data = {
            "canvas": {
                "width": st.session_state.canvas_width,
                "height": st.session_state.canvas_height
            },
            "elements": st.session_state.elements
        }
        st.download_button(
            "Download Prompt",
            json.dumps(export_data, indent=2),
            file_name=f"ui_design_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

# Main canvas area
st.markdown("### Canvas")

# Create the Three.js interactive canvas
threejs_code = '''
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <div id="canvas-container" style="width: 100%; height: 600px; position: relative;">
        <div id="scene-container" style="width: 100%; height: 100%;"></div>
    </div>

    <script>
        // Initialize Three.js scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf5f5f5);
        
        // Orthographic camera for 2D view
        const width = window.innerWidth;
        const height = 600;
        const camera = new THREE.OrthographicCamera(
            width / -2, width / 2,
            height / 2, height / -2,
            1, 1000
        );
        camera.position.z = 100;
        
        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(width, height);
        document.getElementById('scene-container').appendChild(renderer.domElement);
        
        // Track mouse position and dragging state
        let mouse = new THREE.Vector2();
        let dragging = false;
        let selectedObject = null;
        let offset = new THREE.Vector2();
        
        // Create UI elements from session state
        function createUIElements(elements) {
            elements.forEach(element => {
                const geometry = new THREE.PlaneGeometry(element.width, element.height);
                const material = new THREE.MeshBasicMaterial({ 
                    color: 0xffffff,
                    side: THREE.DoubleSide
                });
                const mesh = new THREE.Mesh(geometry, material);
                
                // Position relative to canvas
                mesh.position.x = element.x - width/2 + element.width/2;
                mesh.position.y = -element.y + height/2 - element.height/2;
                mesh.position.z = 0;
                
                mesh.userData = element;
                mesh.userData.isMainElement = true;
                scene.add(mesh);

                // Add resize handles
                const handleSize = 10;
                const handles = [
                    { x: -1, y: -1, cursor: 'nw-resize', type: 'corner' },  // Top-left
                    { x: 1, y: -1, cursor: 'ne-resize', type: 'corner' },   // Top-right
                    { x: -1, y: 1, cursor: 'sw-resize', type: 'corner' },   // Bottom-left
                    { x: 1, y: 1, cursor: 'se-resize', type: 'corner' },    // Bottom-right
                    { x: 0, y: -1, cursor: 'n-resize', type: 'edge' },      // Top
                    { x: 0, y: 1, cursor: 's-resize', type: 'edge' },       // Bottom
                    { x: -1, y: 0, cursor: 'w-resize', type: 'edge' },      // Left
                    { x: 1, y: 0, cursor: 'e-resize', type: 'edge' }        // Right
                ];

                handles.forEach(handleData => {
                    const handleGeometry = new THREE.PlaneGeometry(handleSize, handleSize);
                    const handleMaterial = new THREE.MeshBasicMaterial({
                        color: 0x4a90e2,
                        side: THREE.DoubleSide
                    });
                    const handle = new THREE.Mesh(handleGeometry, handleMaterial);
                    
                    // Position handle relative to main element
                    handle.position.x = mesh.position.x + (handleData.x * element.width/2);
                    handle.position.y = mesh.position.y + (handleData.y * element.height/2);
                    handle.position.z = 1;  // Slightly in front
                    
                    handle.userData = {
                        isHandle: true,
                        parentElement: mesh,
                        handleType: handleData.type,
                        cursor: handleData.cursor,
                        xDir: handleData.x,
                        yDir: handleData.y
                    };
                    
                    scene.add(handle);
                    if (!mesh.userData.handles) mesh.userData.handles = [];
                    mesh.userData.handles.push(handle);
                });
            });
        }
        
        // Track resize state
        let isResizing = false;
        let resizeHandle = null;
        let originalSize = { width: 0, height: 0 };
        let originalPosition = { x: 0, y: 0 };
        let startPoint = { x: 0, y: 0 };
        
        // Mouse event handlers
        renderer.domElement.addEventListener('mousedown', onMouseDown);
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        renderer.domElement.addEventListener('mouseup', onMouseUp);
        
        function onMouseDown(event) {
            event.preventDefault();
            
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, camera);
            
            const intersects = raycaster.intersectObjects(scene.children);
            
            if (intersects.length > 0) {
                const object = intersects[0].object;
                
                if (object.userData.isHandle) {
                    isResizing = true;
                    resizeHandle = object;
                    const parentElement = object.userData.parentElement;
                    
                    originalSize.width = parentElement.userData.width;
                    originalSize.height = parentElement.userData.height;
                    originalPosition.x = parentElement.position.x;
                    originalPosition.y = parentElement.position.y;
                    startPoint.x = intersects[0].point.x;
                    startPoint.y = intersects[0].point.y;
                    
                    // Change cursor based on handle type
                    renderer.domElement.style.cursor = object.userData.cursor;
                } else if (object.userData.isMainElement) {
                    dragging = true;
                    selectedObject = object;
                    
                    const intersectPoint = intersects[0].point;
                    offset.x = selectedObject.position.x - intersectPoint.x;
                    offset.y = selectedObject.position.y - intersectPoint.y;
                    
                    renderer.domElement.style.cursor = 'move';
                }
            }
        }
        
        function onMouseMove(event) {
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, camera);
            
            if (isResizing && resizeHandle) {
                const planeZ = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
                const intersectPoint = new THREE.Vector3();
                raycaster.ray.intersectPlane(planeZ, intersectPoint);
                
                const deltaX = intersectPoint.x - startPoint.x;
                const deltaY = intersectPoint.y - startPoint.y;
                
                const parentElement = resizeHandle.userData.parentElement;
                const { xDir, yDir } = resizeHandle.userData;
                
                // Calculate new size and position
                let newWidth = originalSize.width;
                let newHeight = originalSize.height;
                let newX = originalPosition.x;
                let newY = originalPosition.y;
                
                if (xDir !== 0) {
                    const widthDelta = deltaX * xDir * 2;
                    newWidth = Math.max(50, originalSize.width + widthDelta);
                    if (xDir < 0) {
                        newX = originalPosition.x + (originalSize.width - newWidth) / 2;
                    } else {
                        newX = originalPosition.x + (newWidth - originalSize.width) / 2;
                    }
                }
                
                if (yDir !== 0) {
                    const heightDelta = deltaY * yDir * 2;
                    newHeight = Math.max(50, originalSize.height + heightDelta);
                    if (yDir < 0) {
                        newY = originalPosition.y + (originalSize.height - newHeight) / 2;
                    } else {
                        newY = originalPosition.y + (newHeight - originalSize.height) / 2;
                    }
                }
                
                // Update element geometry
                parentElement.geometry.dispose();
                parentElement.geometry = new THREE.PlaneGeometry(newWidth, newHeight);
                parentElement.position.set(newX, newY, 0);
                
                // Update userData
                parentElement.userData.width = newWidth;
                parentElement.userData.height = newHeight;
                parentElement.userData.x = newX + width/2 - newWidth/2;
                parentElement.userData.y = -newY + height/2 - newHeight/2;
                
                // Update handle positions
                updateHandlePositions(parentElement);
                
            } else if (dragging && selectedObject) {
                const planeZ = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
                const intersectPoint = new THREE.Vector3();
                raycaster.ray.intersectPlane(planeZ, intersectPoint);
                
                selectedObject.position.x = intersectPoint.x + offset.x;
                selectedObject.position.y = intersectPoint.y + offset.y;
                
                // Update element position in userData
                selectedObject.userData.x = selectedObject.position.x + width/2 - selectedObject.userData.width/2;
                selectedObject.userData.y = -selectedObject.position.y + height/2 - selectedObject.userData.height/2;
                
                // Update handle positions
                updateHandlePositions(selectedObject);
            } else {
                // Hover effect
                const intersects = raycaster.intersectObjects(scene.children);
                if (intersects.length > 0) {
                    const object = intersects[0].object;
                    if (object.userData.isHandle) {
                        renderer.domElement.style.cursor = object.userData.cursor;
                    } else if (object.userData.isMainElement) {
                        renderer.domElement.style.cursor = 'move';
                    } else {
                        renderer.domElement.style.cursor = 'default';
                    }
                } else {
                    renderer.domElement.style.cursor = 'default';
                }
            }
        }
        
        function onMouseUp() {
            dragging = false;
            isResizing = false;
            selectedObject = null;
            resizeHandle = null;
            renderer.domElement.style.cursor = 'default';
        }
        
        function updateHandlePositions(element) {
            if (element.userData.handles) {
                element.userData.handles.forEach(handle => {
                    handle.position.x = element.position.x + (handle.userData.xDir * element.userData.width/2);
                    handle.position.y = element.position.y + (handle.userData.yDir * element.userData.height/2);
                });
            }
        }
        
        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        
        // Handle window resize
        window.addEventListener('resize', () => {
            const newWidth = window.innerWidth;
            
            camera.left = newWidth / -2;
            camera.right = newWidth / 2;
            camera.updateProjectionMatrix();
            
            renderer.setSize(newWidth, height);
        });
        
        // Start animation
        animate();
        
        // Create initial elements
        createUIElements(''' + json.dumps(st.session_state.elements) + ''');
    </script>
'''

# Render the Three.js canvas
components.html(threejs_code, height=650) 