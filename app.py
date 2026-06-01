import streamlit as st
import os
import pandas as pd
import time
from model import EngineComponentDataset, generate_model

# Set page configuration as the first Streamlit command
st.set_page_config(page_title="3D Engine Component Generator", layout="wide", initial_sidebar_state="expanded")

# Set paths
# BASE_DIR = r"C:\Users\Sneha Pandey\Desktop\Automated 3d Model generation\Dataset\create dataset python"
# MODEL_DIR = os.path.join(BASE_DIR, "dataset", "models")
# METADATA_FILE = os.path.join(BASE_DIR, "dataset", "metadata.csv")
# OUTPUT_DIR = os.path.join(BASE_DIR, "dataset", "outputs")
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "Data", "stl_models")
METADATA_FILE = os.path.join(BASE_DIR, "Data", "metadata.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize dataset without Streamlit commands
@st.cache_resource
def load_dataset():
    try:
        dataset = EngineComponentDataset(METADATA_FILE, MODEL_DIR)
        missing_files_count = len(dataset.missing_files)
        return dataset, missing_files_count, None
    except Exception as e:
        return None, 0, str(e)

# Load dataset and handle results
dataset, missing_files_count, load_error = load_dataset()

# Handle dataset loading errors after set_page_config
if load_error:
    st.error(f"Failed to load dataset: {load_error}")
    st.stop()

# Removed the warning display as per user request
# if missing_files_count > 0:
#     st.warning(f"Found {missing_files_count} missing files in dataset. Consider regenerating or updating metadata.csv.")

# Enhanced CSS with animations, gradients, and modern styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    body, .stApp {
        background: linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%);
        color: #E0E0E0;
        font-family: 'Poppins', sans-serif;
    }
    h1 {
        color: #4CAF50;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    .stTextInput > div > div > input {
        background-color: #2D2D2D;
        color: #E0E0E0;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 8px;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #66BB6A;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
    }
    .stSelectbox > div > div > select {
        background-color: #2D2D2D;
        color: #E0E0E0;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 8px;
        transition: all 0.3s ease;
    }
    .stSelectbox > div > div > select:focus {
        border-color: #66BB6A;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
    }
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #66BB6A);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: transform 0.2s ease, box-shadow 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.5);
    }
    .stCheckbox > label, .stSlider > label {
        color: #E0E0E0;
        font-weight: 600;
    }
    .stSlider > div > div > div > div {
        background-color: #4CAF50;
    }
    .stExpander {
        background-color: #2D2D2D;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    .splash-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeOut 1s ease-in-out 3s forwards;
    }
    .splash-screen img {
        max-width: 40%;
        max-height: 40%;
        margin-bottom: 20px;
        animation: spin 3s linear infinite;
    }
    .splash-screen h1 {
        color: #4CAF50;
        font-size: 2.5em;
        font-weight: 700;
        animation: bounce 1s ease-in-out;
    }
    @keyframes fadeOut {
        to { opacity: 0; display: none; }
    }
    @keyframes spin {
        100% { transform: rotate(360deg); }
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-20px); }
        60% { transform: translateY(-10px); }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #2D2D2D 0%, #3A3A3A 100%);
        border-right: 2px solid #4CAF50;
        padding: 20px;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.5);
    }
    .result-card {
        background: #2D2D2D;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        animation: fadeIn 0.5s ease-in-out;
    }
    .custom-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    .custom-spinner img {
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
    }
    .stMarkdown, .stSuccess, .stInfo, .stWarning {
        font-family: 'Poppins', sans-serif;
    }
    .stDownloadButton > button {
        background: linear-gradient(45deg, #2196F3, #42A5F5);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 8px 16px;
        transition: transform 0.2s ease;
    }
    .stDownloadButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.5);
    }
    </style>
    <div class="splash-screen">
        <img src="https://cdn-icons-png.flaticon.com/512/0/633.png" alt="Gear Icon">
        <h1>Automated 3D Model Generator</h1>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for generation history
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []
if 'generation_counter' not in st.session_state:
    st.session_state.generation_counter = 1

# Sidebar for controls
with st.sidebar:
    st.header("Generation Controls")
    component = st.selectbox(
        "Component Type",
        ["camshaft", "connecting_rod", "crankshaft", "cylinder_head", "crankcase", "engine_valve"],
        key="component_select",
        help="Select the engine component to generate."
    )
    description = st.text_input(
        "Description",
        placeholder="e.g., 200 mm long connecting rod with 30 mm wide bearing",
        key="description_input",
        help="Enter a description matching metadata.csv for best results."
    )
    save_to_dataset = st.checkbox(
        "Save to Dataset",
        value=False,
        key="save_to_dataset",
        help="Save the generated STL to dataset/models/ and metadata.csv."
    )
    similarity_threshold = st.slider(
        "Similarity Threshold",
        min_value=0.5,
        max_value=1.0,
        value=0.8,
        step=0.05,
        key="similarity_threshold",
        help="Adjust threshold for dataset retrieval (lower for more parametric outputs)."
    )
    generate_button = st.button("Generate STL", key="generate_button")

# Main content
st.title("3D Engine Component Generator")
st.markdown("""
    Generate 3D STL models of engine components from text descriptions. Use the sidebar to input your component type and description, then click 'Generate STL'. View and download all generated models in the history below.
""")

# Handle generation
if generate_button:
    if not description.strip():
        st.error("Description cannot be empty.")
    else:
        # Custom spinner with gear animation
        with st.spinner(""):
            st.markdown("""
                <div class="custom-spinner">
                    <img src="https://cdn-icons-png.flaticon.com/512/0/633.png" alt="Spinning Gear">
                </div>
                <p style="text-align: center; color: #E0E0E0;">Generating 3D model...</p>
            """, unsafe_allow_html=True)
            try:
                output_filename = f"{component}_generated_{st.session_state.generation_counter:03d}.stl"
                output_filepath = os.path.join(OUTPUT_DIR, output_filename)
                # Update dataset's similarity threshold
                dataset.find_nearest_stl = lambda text, comp: EngineComponentDataset.find_nearest_stl(dataset, text, comp, similarity_threshold)
                source_filename, params = generate_model(dataset, description, component, output_path=output_filepath)
                
                # Display success message in a card
                st.markdown(f"""
                    <div class="result-card">
                        <h3 style="color: #4CAF50; margin: 0;">Success!</h3>
                        <p><strong>Generated:</strong> {os.path.abspath(output_filepath)}</p>
                        {"<p><strong>Retrieved from dataset:</strong> " + source_filename + "</p>" if source_filename else "<p><strong>Generated parametrically with parameters:</strong> " + str(params) + "</p>"}
                    </div>
                """, unsafe_allow_html=True)
                
                # Add to generation history
                st.session_state.generation_history.append({
                    "component": component,
                    "description": description,
                    "filepath": output_filepath,
                    "filename": output_filename,
                    "source": source_filename,
                    "params": params,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                st.session_state.generation_counter += 1

                # Provide immediate download link
                if os.path.exists(output_filepath):
                    with open(output_filepath, "rb") as file:
                        st.download_button(
                            label=f"Download {output_filename}",
                            data=file,
                            file_name=output_filename,
                            mime="application/octet-stream",
                            key=f"download_{output_filename}"
                        )
                
                # Save to dataset if checked
                if save_to_dataset:
                    new_filename = f"{component}_{len(os.listdir(MODEL_DIR)) + 1:03d}.stl"
                    new_filepath = os.path.join(MODEL_DIR, new_filename)
                    os.rename(output_filepath, new_filepath)
                    if not os.path.exists(METADATA_FILE):
                        pd.DataFrame(columns=["filename", "component_type", "description"]).to_csv(METADATA_FILE, index=False, encoding="utf-8-sig")
                    new_metadata = pd.DataFrame([{
                        "filename": new_filename,
                        "component_type": component,
                        "description": description
                    }])
                    new_metadata.to_csv(METADATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
                    st.markdown(f"""
                        <div class="result-card">
                            <h3 style="color: #4CAF50; margin: 0;">Saved to Dataset</h3>
                            <p><strong>Saved:</strong> {new_filepath}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    # Update history with new filepath
                    st.session_state.generation_history[-1]["filepath"] = new_filepath
                    st.session_state.generation_history[-1]["filename"] = new_filename
            
            except Exception as e:
                st.error(f"Error generating STL: {e}")
                st.error("Ensure write permissions. Try pausing OneDrive sync or running as Administrator.")

# Generation history
if st.session_state.generation_history:
    st.subheader("Generation History")
    for i, entry in enumerate(st.session_state.generation_history):
        with st.expander(f"Generation {i+1}: {entry['component']} - {entry['description']} ({entry['timestamp']})"):
            st.markdown(f"""
                <div class="result-card">
                    <p><strong>File:</strong> {entry['filename']}</p>
                    <p><strong>Path:</strong> {entry['filepath']}</p>
                    {"<p><strong>Source:</strong> Retrieved from dataset (" + entry['source'] + ")</p>" if entry['source'] else "<p><strong>Source:</strong> Parametric (parameters: " + str(entry['params']) + ")</p>"}
                </div>
            """, unsafe_allow_html=True)
            if os.path.exists(entry['filepath']):
                with open(entry['filepath'], "rb") as file:
                    st.download_button(
                        label=f"Download {entry['filename']}",
                        data=file,
                        file_name=entry['filename'],
                        mime="application/octet-stream",
                        key=f"history_download_{i}"
                    )
            else:
                st.warning("File not found. It may have been moved or deleted.")

# Footer
st.markdown("---")
st.markdown("**Version 1.0 | Built by Sneha Pandey**")
