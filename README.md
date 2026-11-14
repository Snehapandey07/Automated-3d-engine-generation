# ModelForge – Automated 3D Model Generation

Generate parametric 3D models from plain-English descriptions. Type what you need, and ModelForge finds the closest matching model, extracts the dimensions and parameters from your text, and produces a customized STL file you can view in 3D and download.

**Live demo:** https://automated-3d-engine-generation-jlpjs8tgug6ezaekeyukjg.streamlit.app/
*(Streamlit apps go to sleep when unused. If you see an "app is asleep" page, click the wake-up button and wait a moment.)*

## How it works

1. **Input** – the user describes the model in natural language.
2. **Semantic retrieval** – the description and the stored model descriptions are converted to embeddings with DistilBERT, and the closest match is found using cosine similarity.
3. **Parameter extraction** – dimensions and other parameters are extracted from the text.
4. **Model generation** – a customized STL model is generated from the matched model and the extracted parameters.
5. **Visualization and export** – the model is shown in an interactive 3D view (Plotly) and can be downloaded as STL.


## Features

- Natural-language input for 3D model generation
- Semantic search over model descriptions (DistilBERT embeddings + cosine similarity)
- Automatic extraction of dimensions and parameters from text
- Interactive 3D preview
- STL export

## Tech stack

Python, PyTorch, Hugging Face Transformers, Streamlit, Trimesh, Plotly, NumPy, Pandas, Scikit-learn

## Project structure

```
app.py              TODO: confirm – Streamlit app entry point
model.py            TODO: describe what this file does
src/                TODO: describe the modules inside
Data/               TODO: describe the data (what the files are, how they are used)
requirements.txt    Python dependencies
```

## Run locally

```bash
git clone https://github.com/Snehapandey07/Automated-3d-engine-generation.git
cd Automated-3d-engine-generation
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py            # TODO: confirm this is the correct entry point
```

