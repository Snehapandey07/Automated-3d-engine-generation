import streamlit as st
import os
import pandas as pd
import time
from model import EngineComponentDataset, generate_model
import trimesh
import plotly.graph_objects as go

st.set_page_config(
    page_title="3D Engine Component Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "Data", "stl_models")
METADATA_FILE = os.path.join(BASE_DIR, "Data", "metadata.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
#stl viewer
def render_stl_plotly(stl_path):
    try:
        mesh = trimesh.load(stl_path, force='mesh')

        vertices = mesh.vertices
        faces = mesh.faces

        fig = go.Figure(
            data=[
                go.Mesh3d(
                    x=vertices[:, 0],
                    y=vertices[:, 1],
                    z=vertices[:, 2],
                    i=faces[:, 0],
                    j=faces[:, 1],
                    k=faces[:, 2],
                    opacity=1.0,
                    color='lightblue'
                )
            ]
        )

        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"3D preview failed: {e}")

@st.cache_resource
def load_dataset():
    try:
        dataset = EngineComponentDataset(METADATA_FILE, MODEL_DIR)
        missing_files_count = len(dataset.missing_files)
        return dataset, missing_files_count, None
    except Exception as e:
        return None, 0, str(e)

dataset, missing_files_count, load_error = load_dataset()

if load_error:
    st.error(f"Failed to load dataset: {load_error}")
    st.stop()

if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

if 'generation_counter' not in st.session_state:
    st.session_state.generation_counter = 1

st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%);
    color: #E0E0E0;
    font-family: 'Poppins', sans-serif;
}

h1 {
    color: #4CAF50;
    font-weight: 700;
}

.result-card {
    background: #2D2D2D;
    border: 2px solid #4CAF50;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Generation Controls")

    component = st.selectbox(
        "Component Type",
        ["camshaft", "connecting_rod", "crankshaft", "cylinder_head", "crankcase", "engine_valve"]
    )

    description = st.text_input(
        "Description",
        placeholder="e.g., 200 mm long connecting rod"
    )

    save_to_dataset = st.checkbox("Save to Dataset", value=False)

    similarity_threshold = st.slider(
        "Similarity Threshold",
        0.5, 1.0, 0.8, 0.05
    )

    generate_button = st.button("Generate STL")

st.title("3D Engine Component Generator")

st.markdown("""
Generate 3D STL models from text descriptions and visualize them instantly.
""")

if generate_button:

    if not description.strip():
        st.error("Description cannot be empty.")
    else:
        with st.spinner("Generating model..."):

            output_filename = f"{component}_generated_{st.session_state.generation_counter:03d}.stl"
            output_filepath = os.path.join(OUTPUT_DIR, output_filename)

            # override similarity threshold
            dataset.find_nearest_stl = lambda text, comp: EngineComponentDataset.find_nearest_stl(
                dataset, text, comp, similarity_threshold
            )

            source_filename, params = generate_model(
                dataset,
                description,
                component,
                output_path=output_filepath
            )

            st.success("Model Generated Successfully!")

            st.subheader("3D Preview")
            render_stl_plotly(output_filepath)
#download
            if os.path.exists(output_filepath):
                with open(output_filepath, "rb") as file:
                    st.download_button(
                        label="Download STL",
                        data=file,
                        file_name=output_filename,
                        mime="application/octet-stream"
                    )

            # HISTORY
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

            if save_to_dataset:
                new_filename = f"{component}_{len(os.listdir(MODEL_DIR)) + 1:03d}.stl"
                new_filepath = os.path.join(MODEL_DIR, new_filename)

                os.rename(output_filepath, new_filepath)

                if not os.path.exists(METADATA_FILE):
                    pd.DataFrame(columns=["filename", "component_type", "description"]).to_csv(
                        METADATA_FILE, index=False
                    )

                pd.DataFrame([{
                    "filename": new_filename,
                    "component_type": component,
                    "description": description
                }]).to_csv(METADATA_FILE, mode="a", header=False, index=False)

                st.info(f"Saved to dataset: {new_filename}")

                st.session_state.generation_history[-1]["filepath"] = new_filepath
                st.session_state.generation_history[-1]["filename"] = new_filename

if st.session_state.generation_history:

    st.subheader("Generation History")

    for i, entry in enumerate(st.session_state.generation_history):

        with st.expander(f"{entry['component']} - {entry['timestamp']}"):

            st.write("**Description:**", entry['description'])
            st.write("**File:**", entry['filename'])

            # 🔥 3D VIEWER ADDED HERE TOO
            if os.path.exists(entry['filepath']):
                render_stl_plotly(entry['filepath'])

                with open(entry['filepath'], "rb") as file:
                    st.download_button(
                        label="Download STL",
                        data=file,
                        file_name=entry['filename'],
                        mime="application/octet-stream",
                        key=f"dl_{i}"
                    )
            else:
                st.warning("File missing.")
st.markdown("---")
st.markdown("**Version 1.0 | Built by Sneha Pandey**")