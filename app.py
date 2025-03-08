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
            st.experimental_rerun()

    # Clear canvas button
    if st.button("Clear Canvas"):
        st.session_state.elements = []
        st.experimental_rerun()

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

# Generate HTML for each element
elements_html = ""
for element in st.session_state.elements:
    style = f"""
        left: {element['x']}px;
        top: {element['y']}px;
        width: {element['width']}px;
        height: {element['height']}px;
    """
    
    content = ""
    if element['type'] == 'Button':
        content = f'<button style="width: 100%; height: 100%; cursor: pointer">{element["text"]}</button>'
    elif element['type'] == 'Text Input':
        content = f'<input type="text" placeholder="{element["text"]}" style="width: 100%">'
    elif element['type'] == 'Dropdown':
        options = ''.join([f'<option>{opt}</option>' for opt in element['options']])
        content = f'<select style="width: 100%">{options}</select>'
    elif element['type'] == 'Window':
        content = f'''
            <div style="width: 100%; height: 100%; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="padding: 8px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; border-radius: 8px 8px 0 0;">
                    Window Title
                </div>
                <div style="padding: 16px;">Window Content</div>
            </div>
        '''
    elif element['type'] == 'Sidebar':
        content = f'''
            <div style="width: 100%; height: 100%; background: #f8f9fa; border-right: 1px solid #dee2e6; padding: 16px;">
                Sidebar Content
            </div>
        '''
    else:
        content = f'<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">{element["type"]}</div>'
    
    elements_html += f'<div class="ui-element" style="{style}">{content}</div>'

# Render canvas with elements
canvas_html = f"""
<div class="canvas" style="width: {st.session_state.canvas_width}px; height: {st.session_state.canvas_height}px">
    {elements_html}
</div>
"""

components.html(canvas_html, height=st.session_state.canvas_height + 40)

st.title("Three.js in Streamlit Demo")

# HTML component with Three.js scene
components.html('''
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    
    <div id="scene-container" style="height: 400px;"></div>
    
    <script>
        // Set up scene
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        
        // Create renderer
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, 400);
        document.getElementById('scene-container').appendChild(renderer.domElement);
        
        // Create a cube
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        
        // Add lights
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(1, 1, 1);
        scene.add(light);
        
        const ambientLight = new THREE.AmbientLight(0x404040);
        scene.add(ambientLight);
        
        // Position camera
        camera.position.z = 5;
        
        // Animation function
        function animate() {
            requestAnimationFrame(animate);
            
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            
            renderer.render(scene, camera);
        }
        
        // Handle window resize
        window.addEventListener('resize', onWindowResize, false);
        
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, 400);
        }
        
        animate();
    </script>
''', height=450) 