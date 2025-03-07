import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import os

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
        width = st.slider("Width", 50, 800, 200)
        height = st.slider("Height", 50, 600, 200)
        
        if selected_tool in ["Button", "Text Input"]:
            text = st.text_input("Label", "New " + selected_tool)
        
        if selected_tool == "Dropdown":
            options = st.text_area("Options (one per line)", "Option 1\nOption 2\nOption 3")

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

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "frontend")

# Initialize the React component
canvas_component = components.declare_component(
    "canvas_component",
    path=frontend_path
)

# Call the React component
canvas_result = canvas_component(
    selectedTool=selected_tool,
    toolProperties={
        "width": width if 'width' in locals() else 200,
        "height": height if 'height' in locals() else 200,
        "text": text if 'text' in locals() else "",
        "options": options.split('\n') if 'options' in locals() else []
    }
)

# Handle the result from React
if canvas_result:
    if canvas_result['type'] == 'add':
        st.session_state.elements.append(canvas_result['element'])
    elif canvas_result['type'] == 'move':
        # Update element position
        for i, element in enumerate(st.session_state.elements):
            if element['id'] == canvas_result['element']['id']:
                st.session_state.elements[i] = canvas_result['element']
                break 