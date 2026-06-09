print("NEW MODEL.PY LOADED")
import os
import re
import numpy as np
import pandas as pd
import trimesh
import torch
from transformers import DistilBertTokenizer, DistilBertModel
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import logging
import math
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "Data", "stl_models")
METADATA_FILE = os.path.join(BASE_DIR, "Data", "metadata.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("MODEL_DIR =", MODEL_DIR)
print("METADATA_FILE =", METADATA_FILE)
print("OUTPUT_DIR =", OUTPUT_DIR)

device = torch.device("cpu")
logging.info(f"Using device: {device}")
\
def generate_connecting_rod(params):
    length = params.get("length", 150.0)
    width = params.get("width", 20.0)
    thickness = params.get("thickness", 10.0)
    bearing_diameter = params.get("bearing_diameter", 30.0)

    # Create main rod body
    body_vertices = [
        [0, -width/2, -thickness/2], [0, width/2, -thickness/2], [0, width/2, thickness/2], [0, -width/2, thickness/2],
        [length, -width/2, -thickness/2], [length, width/2, -thickness/2], [length, width/2, thickness/2], [length, -width/2, thickness/2]
    ]
    body_faces = [
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]
    ]
    body_mesh = trimesh.Trimesh(vertices=body_vertices, faces=body_faces)

    # Add bearing holes 
    segments = 32
    bearing_vertices = []
    bearing_faces = []
    for z in [-thickness/2, thickness/2]:
        for i in range(2):  # Two bearings
            center_x = i * length
            for j in range(segments):
                angle = j * 2 * math.pi / segments
                x = center_x + (bearing_diameter/2) * math.cos(angle)
                y = (bearing_diameter/2) * math.sin(angle)
                bearing_vertices.append([x, y, z])

    for i in range(segments):
        v0 = i
        v1 = (i + 1) % segments
        v2 = segments + i
        v3 = segments + (i + 1) % segments
        bearing_faces.append([v0, v1, v3])
        bearing_faces.append([v0, v3, v2])
        v0 = 2 * segments + i
        v1 = 2 * segments + (i + 1) % segments
        v2 = 3 * segments + i
        v3 = 3 * segments + (i + 1) % segments
        bearing_faces.append([v0, v1, v3])
        bearing_faces.append([v0, v3, v2])

    bearing_mesh = trimesh.Trimesh(vertices=bearing_vertices, faces=bearing_faces)
    mesh = body_mesh + bearing_mesh  # Combine meshes
    return mesh

def generate_camshaft(params):
    length = params.get("length", 500.0)
    diameter = params.get("diameter", 20.0)
    lobe_count = params.get("lobe_count", 8)
    lobe_height = params.get("lobe_height", 10.0)

    vertices = []
    faces = []
    segments = 32
    z_step = length / (lobe_count + 1)
    angle_step = 2 * math.pi / segments

    for i in range(lobe_count + 2):
        z = i * z_step
        is_lobe = i > 0 and i <= lobe_count
        radius = (diameter / 2) + (lobe_height if is_lobe else 0)
        for j in range(segments):
            angle = j * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append([x, y, z])

    for i in range(lobe_count + 1):
        for j in range(segments):
            v0 = i * segments + j
            v1 = i * segments + (j + 1) % segments
            v2 = (i + 1) * segments + j
            v3 = (i + 1) * segments + (j + 1) % segments
            faces.append([v0, v1, v3])
            faces.append([v0, v3, v2])

    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_crankshaft(params):
    length = params.get("length", 600.0)
    diameter = params.get("diameter", 30.0)
    throw_count = params.get("throw_count", 4)
    vertices = []
    faces = []
    segments = 32
    z_step = length / (throw_count + 1)
    angle_step = 2 * math.pi / segments
    for i in range(throw_count + 2):
        z = i * z_step
        radius = diameter / 2
        for j in range(segments):
            angle = j * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) + (20.0 if i % 2 == 1 else 0)
            vertices.append([x, y, z])
    for i in range(throw_count + 1):
        for j in range(segments):
            v0 = i * segments + j
            v1 = i * segments + (j + 1) % segments
            v2 = (i + 1) * segments + j
            v3 = (i + 1) * segments + (j + 1) % segments
            faces.append([v0, v1, v3])
            faces.append([v0, v3, v2])
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_cylinder_head(params):
    length = params.get("length", 200.0)
    width = params.get("width", 150.0)
    height = params.get("height", 50.0)
    vertices = [
        [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
        [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
    ]
    faces = [
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]
    ]
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_crankcase(params):
    length = params.get("length", 300.0)
    width = params.get("width", 200.0)
    height = params.get("height", 100.0)
    vertices = [
        [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
        [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
    ]
    faces = [
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]
    ]
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_engine_valve(params):
    length = params.get("length", 100.0)
    diameter = params.get("diameter", 10.0)
    vertices = []
    faces = []
    segments = 32
    angle_step = 2 * math.pi / segments
    for i in range(2):
        z = i * length
        radius = diameter / 2
        for j in range(segments):
            angle = j * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append([x, y, z])
    for j in range(segments):
        v0 = j
        v1 = (i + 1) % segments
        v2 = segments + j
        v3 = segments + (j + 1) % segments
        faces.append([v0, v1, v3])
        faces.append([v0, v3, v2])
    return trimesh.Trimesh(vertices=vertices, faces=faces)

# Dataset class
class EngineComponentDataset:
    def __init__(self, metadata_file, model_dir):
        self.metadata = pd.read_csv(metadata_file)
        self.model_dir = model_dir
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.bert_model = DistilBertModel.from_pretrained('distilbert-base-uncased').to(device)
        self.bert_model.eval()
        self.label_encoder = LabelEncoder()
        # Filter out NaN component types
        self.metadata = self.metadata[self.metadata['component_type'].notna()]
        self.metadata['component_type'] = self.label_encoder.fit_transform(self.metadata['component_type'])
        self.valid_data, self.missing_files = self._validate_files()
        self.embeddings = self._generate_embeddings()

    def _validate_files(self):
        valid_data = []
        missing_files = []
        component_counts = {comp: 0 for comp in self.metadata['component_type'].unique()}
        for idx, row in self.metadata.iterrows():
            filename = row['filename']
            component_type = row['component_type']
            file_path = os.path.join(self.model_dir, filename)
            try:
                if not os.path.exists(file_path):
                    missing_files.append((filename, self.label_encoder.inverse_transform([component_type])[0]))
                    continue
                mesh = trimesh.load(file_path)
                if mesh.is_empty:
                    logging.warning(f"Empty mesh: {filename}")
                    continue
                valid_data.append(row)
                component_counts[component_type] = component_counts.get(component_type, 0) + 1
            except Exception as e:
                logging.warning(f"Skipping {filename}: {e}")
                missing_files.append((filename, self.label_encoder.inverse_transform([component_type])[0]))
        valid_data = pd.DataFrame(valid_data)
        logging.info(f"Valid files: {len(valid_data)}/{len(self.metadata)}")
        logging.info(f"Component counts: {dict((self.label_encoder.inverse_transform([k])[0], v) for k, v in component_counts.items())}")
        if missing_files:
            logging.warning(f"Missing files: {len(missing_files)}")
            for fname, ctype in missing_files:
                logging.warning(f"Missing: {fname} ({ctype})")
        return valid_data, missing_files

    def _generate_embeddings(self):
        embeddings = []
        for _, row in self.valid_data.iterrows():
            description = row['description']
            component_type = row['component_type']
            inputs = self.tokenizer(description, return_tensors='pt', max_length=128, padding='max_length', truncation=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            text_embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
            component_one_hot = np.zeros(len(self.label_encoder.classes_))
            component_one_hot[component_type] = 1
            embedding = np.concatenate([text_embedding, component_one_hot])
            embeddings.append(embedding)
        return np.array(embeddings)

    def find_nearest_stl(self, text, component_type, similarity_threshold=0.8):
        try:
            component_idx = self.label_encoder.transform([component_type])[0]
        except ValueError:
            logging.error(f"Invalid component type: {component_type}")
            raise ValueError(f"Component type must be one of: {self.label_encoder.classes_}")

        inputs = self.tokenizer(text, return_tensors='pt', max_length=128, padding='max_length', truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        text_embedding = outputs.last_hidden_state[:, 0, :].squeeze().cpu().numpy()
        component_one_hot = np.zeros(len(self.label_encoder.classes_))
        component_one_hot[component_idx] = 1
        query_embedding = np.concatenate([text_embedding, component_one_hot])

        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        max_similarity = np.max(similarities)
        if max_similarity < similarity_threshold:
            logging.info(f"No close match found (max similarity: {max_similarity:.2f}). Using parametric generation.")
            params = self.extract_parameters(text, component_type)
            if component_type == "connecting_rod":
                mesh = generate_connecting_rod(params)
            elif component_type == "camshaft":
                mesh = generate_camshaft(params)
            elif component_type == "crankshaft":
                mesh = generate_crankshaft(params)
            elif component_type == "cylinder_head":
                mesh = generate_cylinder_head(params)
            elif component_type == "crankcase":
                mesh = generate_crankcase(params)
            elif component_type == "engine_valve":
                mesh = generate_engine_valve(params)
            else:
                raise ValueError(f"Parametric generation not implemented for {component_type}")
            return mesh, None, params

        idx = np.argmax(similarities)
        filename = self.valid_data.iloc[idx]['filename']
        mesh = trimesh.load(os.path.join(self.model_dir, filename))
        return mesh, filename, None

    def extract_parameters(self, text, component_type):
        params = {}
        text = text.lower()
        def convert_length(value, unit):
            if unit == "cm":
                return value * 10.0
            elif unit == "m":
                return value * 1000.0
            return value

        if component_type == "connecting_rod":
            length_match = re.search(r'(\d+(\.\d+)?)\s*(mm|cm|m)?\s*(long|length)', text)
            width_match = re.search(r'(\d+(\.\d+)?)\s*(mm|cm)?\s*(wide|width)', text)
            bearing_match = re.search(r'(\d+(\.\d+)?)\s*(mm|cm)?\s*(bearing|hole)', text)
            params["length"] = convert_length(float(length_match.group(1)), length_match.group(3)) if length_match else (200.0 if "long" in text else 150.0)
            params["width"] = convert_length(float(width_match.group(1)), width_match.group(3)) if width_match else (25.0 if "wide" in text else 20.0)
            params["thickness"] = 15.0 if "thick" in text else 10.0
            params["bearing_diameter"] = convert_length(float(bearing_match.group(1)), bearing_match.group(3)) if bearing_match else (35.0 if "large bearing" in text else 30.0)
        elif component_type == "camshaft":
            length_match = re.search(r'(\d+(\.\d+)?)\s*(mm|cm|m)?\s*(long|length)', text)
            lobe_match = re.search(r'(\d+)\s*(lobes?|cams?)', text)
            diameter_match = re.search(r'(\d+(\.\d+)?)\s*(mm|cm)?\s*(diameter|thick|thin)', text)
            params["length"] = convert_length(float(length_match.group(1)), length_match.group(3)) if length_match else (600.0 if "long" in text else 400.0)
            params["lobe_count"] = int(lobe_match.group(1)) if lobe_match else (12 if "many lobes" in text else 8)
            params["diameter"] = convert_length(float(diameter_match.group(1)), diameter_match.group(3)) if diameter_match else (25.0 if "thick" in text else 20.0)
            params["lobe_height"] = 15.0 if any(k in text for k in ["big cams", "large lobes"]) else 10.0
        # Add other components similarly (omitted for brevity)
        return params

def generate_model(dataset, text, component_type, output_path="generated.stl", max_retries=3):
    valid_components = ["camshaft", "connecting_rod", "crankshaft", "cylinder_head", "crankcase", "engine_valve"]
    if component_type not in valid_components:
        raise ValueError(f"Component type must be one of: {valid_components}")

    for attempt in range(max_retries):
        try:
            mesh, source_filename, params = dataset.find_nearest_stl(text, component_type)
            mesh.export(output_path)
            if source_filename:
                logging.info(f"Generated STL from dataset: {source_filename} saved at: {output_path}")
            else:
                logging.info(f"Generated parametric STL with parameters: {params} saved at: {output_path}")
            return source_filename, params
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Retry {attempt+1}/{max_retries} for {output_path}: {e}")
                time.sleep(1)
            else:
                logging.error(f"Error generating STL after {max_retries} retries: {e}")
                raise

def main():
    # Load dataset
    try:
        dataset = EngineComponentDataset(METADATA_FILE, MODEL_DIR)
        if len(dataset.valid_data) == 0:
            logging.error("No valid files found in dataset. Please check STL files and metadata.")
            return
        if len(dataset.missing_files) > 0:
            logging.warning(f"Found {len(dataset.missing_files)} missing files. Consider regenerating or updating metadata.csv.")
    except Exception as e:
        logging.error(f"Failed to load dataset: {e}")
        return

    valid_components = ["camshaft", "connecting_rod", "crankshaft", "cylinder_head", "crankcase", "engine_valve"]
    print("Valid component types:", ", ".join(valid_components))
    
    counter = 1
    while True:
        component_type = input("Enter component type (or 'exit' to quit): ").strip().lower()
        if component_type == 'exit':
            print("Exiting program.")
            break
        if component_type not in valid_components:
            print(f"Error: Component type must be one of: {', '.join(valid_components)}")
            continue

        text = input("Enter description (e.g., '200 mm long connecting rod with 30 mm wide bearing'): ").strip()
        if not text:
            print("Error: Description cannot be empty.")
            continue

        output_filename = f"{component_type}_generated_{counter:03d}.stl"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        try:
            source_filename, params = generate_model(dataset, text, component_type, output_path=output_path)
            print(f"Success: STL generated at {output_path}")
            if source_filename:
                print(f"Retrieved from dataset: {source_filename}")
            else:
                print(f"Generated parametrically with parameters: {params}")
            counter += 1
        except Exception as e:
            print(f"Error: Failed to generate STL: {e}")
        
        continue_prompt = input("Generate another STL? (yes/no): ").strip().lower()
        if continue_prompt not in ['yes', 'y']:
            print("Exiting program.")
            break

if __name__ == "__main__":
    main()