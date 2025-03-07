import streamlit as st
import streamlit.components.v1 as components
import json

# Page config
st.set_page_config(
    page_title="UI to Prompt Designer",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    # Export button
    if st.button("Export Design"):
        # TODO: Get data from React component and format it
        st.download_button(
            "Download Prompt",
            "Exported design data will go here",
            file_name="ui_design_prompt.txt"
        )

# Main canvas area
st.markdown("### Canvas")

# Initialize the React component
canvas_component = components.declare_component(
    "canvas_component",
    path="frontend/build"  # Path to your built React component
)

# Call the React component
canvas_result = canvas_component(
    selected_tool=selected_tool,
    tool_properties={
        "width": width if 'width' in locals() else 200,
        "height": height if 'height' in locals() else 200,
        "text": text if 'text' in locals() else "",
        "options": options.split('\n') if 'options' in locals() else []
    }
)

# Handle the result from React
if canvas_result:
    st.write("Canvas update:", canvas_result) 