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
    st.session_state.background_color = "#f5f5f5"  # Default background color

# Predefined color schemes
COLOR_SCHEMES = {
    "Modern": {
        "Window": "#ffffff",
        "Sidebar": "#f8f9fa",
        "Button": "#007bff",
        "Text Input": "#e9ecef",
        "Dropdown": "#ffffff",
        "Select Box": "#ffffff",
        "Background": "#f5f5f5"
    },
    "Dark": {
        "Window": "#2c3e50",
        "Sidebar": "#34495e",
        "Button": "#3498db",
        "Text Input": "#465c6e",
        "Dropdown": "#2c3e50",
        "Select Box": "#2c3e50",
        "Background": "#1a1a1a"
    },
    "Pastel": {
        "Window": "#f7e9e3",
        "Sidebar": "#e3f7f5",
        "Button": "#c9e4de",
        "Text Input": "#f7d9c4",
        "Dropdown": "#f2e9e4",
        "Select Box": "#e9f2f4",
        "Background": "#fdf6f0"
    }
}

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
    
    # Color scheme selection
    selected_scheme = st.selectbox(
        "Color Scheme",
        ["Modern", "Dark", "Pastel", "Custom"]
    )
    
    # Background color selection
    st.subheader("Canvas Background")
    if selected_scheme == "Custom":
        new_bg_color = st.color_picker("Background Color", st.session_state.background_color)
    else:
        new_bg_color = COLOR_SCHEMES[selected_scheme]["Background"]
    
    if new_bg_color != st.session_state.background_color:
        st.session_state.background_color = new_bg_color
        st.rerun()
    
    # Custom color picker if "Custom" is selected
    if selected_scheme == "Custom":
        element_color = st.color_picker("Element Color", "#ffffff")
        handle_color = st.color_picker("Handle Color", "#4a90e2")
    else:
        element_color = None
        handle_color = "#4a90e2"
    
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
                "options": options.split('\n') if 'options' in locals() else [],
                "color": element_color if selected_scheme == "Custom" else COLOR_SCHEMES[selected_scheme][selected_tool]
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

# Create the Three.js interactive canvas with state management
threejs_code = '''
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <div id="canvas-container" style="width: 100%; height: 600px; position: relative; border: 2px dashed #ccc;">
        <div id="scene-container" style="width: 100%; height: 100%; position: absolute;"></div>
    </div>

    <script>
        // Global state management
        window.threeJsState = window.threeJsState || {
            scene: null,
            camera: null,
            renderer: null,
            elements: new Map(),
            initialized: false,
            background: null
        };

        // Helper function to convert hex color to THREE.Color
        function hexToRgb(hex) {
            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16) / 255,
                g: parseInt(result[2], 16) / 255,
                b: parseInt(result[3], 16) / 255
            } : null;
        }

        // Function to create or update background
        function updateBackground(color) {
            const bgColor = hexToRgb(color);
            
            if (!window.threeJsState.background) {
                // Create background plane that's larger than the visible area
                const bgGeometry = new THREE.PlaneGeometry(2000, 2000);
                const bgMaterial = new THREE.MeshBasicMaterial({
                    color: new THREE.Color(bgColor.r, bgColor.g, bgColor.b),
                    side: THREE.DoubleSide
                });
                window.threeJsState.background = new THREE.Mesh(bgGeometry, bgMaterial);
                window.threeJsState.background.position.z = -10; // Behind everything
                window.threeJsState.scene.add(window.threeJsState.background);
            } else {
                // Update existing background color
                window.threeJsState.background.material.color.setRGB(bgColor.r, bgColor.g, bgColor.b);
            }
        }

        // Initialize scene only if not already initialized
        if (!window.threeJsState.initialized) {
            const container = document.getElementById('scene-container');
            const containerRect = container.getBoundingClientRect();
            
            // Initialize Three.js scene
            window.threeJsState.scene = new THREE.Scene();
            
            // Orthographic camera for 2D view
            const aspect = containerRect.width / containerRect.height;
            window.threeJsState.camera = new THREE.OrthographicCamera(
                -containerRect.width / 2,
                containerRect.width / 2,
                containerRect.height / 2,
                -containerRect.height / 2,
                1,
                1000
            );
            window.threeJsState.camera.position.z = 100;
            
            // Renderer setup
            window.threeJsState.renderer = new THREE.WebGLRenderer({ 
                antialias: true,
                alpha: true 
            });
            window.threeJsState.renderer.setSize(containerRect.width, containerRect.height);
            window.threeJsState.renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(window.threeJsState.renderer.domElement);

            window.threeJsState.initialized = true;
        }

        // Update or create background
        updateBackground("''' + st.session_state.background_color + '''");

        // Function to create or update UI elements
        function updateUIElements(elements) {
            const width = window.innerWidth;
            const height = 600;
            const currentIds = new Set(elements.map(e => e.id));
            
            // Remove elements that no longer exist
            for (let [id, obj] of window.threeJsState.elements) {
                if (!currentIds.has(id)) {
                    // Remove handles
                    if (obj.userData.handles) {
                        obj.userData.handles.forEach(handle => {
                            window.threeJsState.scene.remove(handle);
                        });
                    }
                    // Remove main element
                    window.threeJsState.scene.remove(obj);
                    window.threeJsState.elements.delete(id);
                }
            }

            // Create or update elements
            elements.forEach(element => {
                if (!window.threeJsState.elements.has(element.id)) {
                    // Create new element
                    const geometry = new THREE.PlaneGeometry(element.width, element.height);
                    const color = hexToRgb(element.color || '#ffffff');
                    const material = new THREE.MeshBasicMaterial({ 
                        color: new THREE.Color(color.r, color.g, color.b),
                        side: THREE.DoubleSide
                    });
                    const mesh = new THREE.Mesh(geometry, material);
                    
                    mesh.position.x = element.x - width/2 + element.width/2;
                    mesh.position.y = -element.y + height/2 - element.height/2;
                    mesh.position.z = 0;
                    
                    mesh.userData = element;
                    mesh.userData.isMainElement = true;
                    window.threeJsState.scene.add(mesh);
                    window.threeJsState.elements.set(element.id, mesh);

                    // Add resize handles for new element
                    const handleSize = 8;
                    const handles = [
                        { x: -1, y: -1, cursor: 'nw-resize', type: 'corner' },
                        { x: 1, y: -1, cursor: 'ne-resize', type: 'corner' },
                        { x: -1, y: 1, cursor: 'sw-resize', type: 'corner' },
                        { x: 1, y: 1, cursor: 'se-resize', type: 'corner' },
                        { x: 0, y: -1, cursor: 'n-resize', type: 'edge' },
                        { x: 0, y: 1, cursor: 's-resize', type: 'edge' },
                        { x: -1, y: 0, cursor: 'w-resize', type: 'edge' },
                        { x: 1, y: 0, cursor: 'e-resize', type: 'edge' }
                    ];

                    mesh.userData.handles = [];
                    handles.forEach(handleData => {
                        const handleGeometry = new THREE.PlaneGeometry(handleSize, handleSize);
                        const handleMaterial = new THREE.MeshBasicMaterial({
                            color: 0x4a90e2,
                            side: THREE.DoubleSide,
                            transparent: true,
                            opacity: 0.8
                        });
                        const handle = new THREE.Mesh(handleGeometry, handleMaterial);
                        
                        handle.position.x = mesh.position.x + (handleData.x * element.width/2);
                        handle.position.y = mesh.position.y + (handleData.y * element.height/2);
                        handle.position.z = 1;
                        
                        handle.userData = {
                            isHandle: true,
                            parentElement: mesh,
                            handleType: handleData.type,
                            cursor: handleData.cursor,
                            xDir: handleData.x,
                            yDir: handleData.y
                        };
                        
                        window.threeJsState.scene.add(handle);
                        mesh.userData.handles.push(handle);
                    });
                }
            });
        }

        // Track resize state
        let isResizing = false;
        let resizeHandle = null;
        let originalSize = { width: 0, height: 0 };
        let originalPosition = { x: 0, y: 0 };
        let startPoint = { x: 0, y: 0 };
        
        // Track mouse position and dragging state
        let mouse = new THREE.Vector2();
        let dragging = false;
        let selectedObject = null;
        let offset = new THREE.Vector2();
        
        // Mouse event handlers
        window.threeJsState.renderer.domElement.addEventListener('mousedown', onMouseDown);
        window.threeJsState.renderer.domElement.addEventListener('mousemove', onMouseMove);
        window.threeJsState.renderer.domElement.addEventListener('mouseup', onMouseUp);
        
        function onMouseDown(event) {
            event.preventDefault();
            
            const rect = window.threeJsState.renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, window.threeJsState.camera);
            
            const intersects = raycaster.intersectObjects(window.threeJsState.scene.children);
            
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
                    window.threeJsState.renderer.domElement.style.cursor = object.userData.cursor;
                } else if (object.userData.isMainElement) {
                    dragging = true;
                    selectedObject = object;
                    
                    const intersectPoint = intersects[0].point;
                    offset.x = selectedObject.position.x - intersectPoint.x;
                    offset.y = selectedObject.position.y - intersectPoint.y;
                    
                    window.threeJsState.renderer.domElement.style.cursor = 'move';
                }
            }
        }
        
        function onMouseMove(event) {
            const rect = window.threeJsState.renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, window.threeJsState.camera);
            
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
                
                // Update element geometry and position
                parentElement.geometry.dispose();
                parentElement.geometry = new THREE.PlaneGeometry(newWidth, newHeight);
                parentElement.position.set(newX, newY, 0);
                
                // Update element userData
                parentElement.userData.width = newWidth;
                parentElement.userData.height = newHeight;
                parentElement.userData.x = newX + containerRect.width/2 - newWidth/2;
                parentElement.userData.y = -newY + containerRect.height/2 - newHeight/2;
                
                // Update handle positions
                if (parentElement.userData.handles) {
                    parentElement.userData.handles.forEach(handle => {
                        handle.position.x = parentElement.position.x + (handle.userData.xDir * newWidth/2);
                        handle.position.y = parentElement.position.y + (handle.userData.yDir * newHeight/2);
                    });
                }
                
            } else if (dragging && selectedObject) {
                const planeZ = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
                const intersectPoint = new THREE.Vector3();
                raycaster.ray.intersectPlane(planeZ, intersectPoint);
                
                // Update main element position
                selectedObject.position.x = intersectPoint.x + offset.x;
                selectedObject.position.y = intersectPoint.y + offset.y;
                
                // Update element userData
                selectedObject.userData.x = selectedObject.position.x + containerRect.width/2 - selectedObject.userData.width/2;
                selectedObject.userData.y = -selectedObject.position.y + containerRect.height/2 - selectedObject.userData.height/2;
                
                // Update handle positions
                if (selectedObject.userData.handles) {
                    selectedObject.userData.handles.forEach(handle => {
                        handle.position.x = selectedObject.position.x + (handle.userData.xDir * selectedObject.userData.width/2);
                        handle.position.y = selectedObject.position.y + (handle.userData.yDir * selectedObject.userData.height/2);
                    });
                }
            } else {
                // Hover effect
                const intersects = raycaster.intersectObjects(window.threeJsState.scene.children);
                if (intersects.length > 0) {
                    const object = intersects[0].object;
                    if (object.userData.isHandle) {
                        window.threeJsState.renderer.domElement.style.cursor = object.userData.cursor;
                    } else if (object.userData.isMainElement) {
                        window.threeJsState.renderer.domElement.style.cursor = 'move';
                    } else {
                        window.threeJsState.renderer.domElement.style.cursor = 'default';
                    }
                } else {
                    window.threeJsState.renderer.domElement.style.cursor = 'default';
                }
            }
        }
        
        function onMouseUp() {
            dragging = false;
            isResizing = false;
            selectedObject = null;
            resizeHandle = null;
            window.threeJsState.renderer.domElement.style.cursor = 'default';
        }
        
        // Helper function to update handle positions
        function updateHandlePositions(element) {
            if (element.userData.handles) {
                element.userData.handles.forEach(handle => {
                    handle.position.x = element.position.x + (handle.userData.xDir * element.userData.width/2);
                    handle.position.y = element.position.y + (handle.userData.yDir * element.userData.height/2);
                });
            }
        }

        // Update elements without recreating the scene
        updateUIElements(''' + json.dumps(st.session_state.elements) + ''');

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            window.threeJsState.renderer.render(window.threeJsState.scene, window.threeJsState.camera);
        }
        animate();

        // Handle window resize
        function onWindowResize() {
            const container = document.getElementById('scene-container');
            const containerRect = container.getBoundingClientRect();
            
            window.threeJsState.camera.left = -containerRect.width / 2;
            window.threeJsState.camera.right = containerRect.width / 2;
            window.threeJsState.camera.top = containerRect.height / 2;
            window.threeJsState.camera.bottom = -containerRect.height / 2;
            window.threeJsState.camera.updateProjectionMatrix();
            
            window.threeJsState.renderer.setSize(containerRect.width, containerRect.height);
        }
        
        window.addEventListener('resize', onWindowResize);
    </script>
'''

# Render the Three.js canvas
components.html(threejs_code, height=650) 