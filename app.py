import streamlit as st
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
            background-color: white;
            border: 2px dashed #ccc;
            position: relative;
            margin: 20px;
            min-height: 600px;
        }
        .ui-element {
            position: absolute;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px;
            cursor: move;
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
        content = f'<button style="width: 100%; height: 100%">{element["text"]}</button>'
    elif element['type'] == 'Text Input':
        content = f'<input type="text" placeholder="{element["text"]}" style="width: 100%">'
    elif element['type'] == 'Dropdown':
        options = ''.join([f'<option>{opt}</option>' for opt in element['options']])
        content = f'<select style="width: 100%">{options}</select>'
    else:
        content = f'<div>{element["type"]}</div>'
    
    elements_html += f'<div class="ui-element" style="{style}">{content}</div>'

# Render canvas with elements
canvas_html = f"""
<div class="canvas" style="width: {st.session_state.canvas_width}px; height: {st.session_state.canvas_height}px">
    {elements_html}
</div>
"""

st.components.v1.html(canvas_html, height=st.session_state.canvas_height + 40) 