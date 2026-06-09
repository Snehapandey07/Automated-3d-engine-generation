import trimesh
import pandas as pd
import numpy as np
import os
import tempfile
import shutil

# Set absolute paths
BASE_DIR = r"C:\Users\Sneha Pandey\OneDrive\Desktop\Automated 3d Model generation\Dataset\create dataset python"
METADATA_FILE = os.path.join(BASE_DIR, "dataset", "metadata.csv")
MODELS_DIR = os.path.join(BASE_DIR, "dataset", "models")
TEMP_FILE = os.path.join(tempfile.gettempdir(), "temp_metadata.csv")

# Function to parse description and set parameters
def parse_description(description):
    description = description.lower().strip()
    
    # Default values (in mm)
    params = {
        "shaft_length": 400.0,
        "shaft_diameter": 25.0,
        "cam_major_diameter": 40.0,
        "cam_minor_diameter": 30.0,
        "cam_thickness": 15.0,
        "journal_diameter": 30.0,
        "journal_thickness": 20.0,
        "num_cams": 8
    }
    
    # Keyword-based adjustments
    if "long" in description:
        params["shaft_length"] = 500.0
    elif "short" in description:
        params["shaft_length"] = 300.0
        
    if "big" in description or "large" in description:
        params["cam_major_diameter"] = 50.0
        params["cam_minor_diameter"] = 35.0
    elif "small" in description:
        params["cam_major_diameter"] = 35.0
        params["cam_minor_diameter"] = 25.0
        
    if "thick" in description:
        params["cam_thickness"] = 20.0
        params["journal_thickness"] = 25.0
    elif "thin" in description:
        params["cam_thickness"] = 10.0
        params["journal_thickness"] = 15.0
        
    if "wide" in description:
        params["journal_diameter"] = 35.0
    elif "narrow" in description:
        params["journal_diameter"] = 25.0
    
    # Geometric constraints
    if params["cam_major_diameter"] <= params["cam_minor_diameter"]:
        params["cam_major_diameter"] = params["cam_minor_diameter"] + 5.0
        print(f"Cam major diameter adjusted to {params['cam_major_diameter']} mm.")
    
    if params["journal_diameter"] < params["shaft_diameter"]:
        params["journal_diameter"] = params["shaft_diameter"] + 5.0
        print(f"Journal diameter adjusted to {params['journal_diameter']} mm.")
    
    if params["shaft_length"] < (params["num_cams"] * params["cam_thickness"] + 4 * params["journal_thickness"] + 50):
        params["shaft_length"] = (params["num_cams"] * params["cam_thickness"] + 4 * params["journal_thickness"] + 50)
        print(f"Shaft length adjusted to {params['shaft_length']} mm.")
    
    return params

#  50 parameter combinations matching existing STL files
descriptions = [
    # First 6 (original)
    "long thick camshaft with big cams",
    "short thin camshaft with small cams",
    "long camshaft with narrow journals",
    "short camshaft with wide journals",
    "thick camshaft",
    "thin camshaft with big cams",
    # Next 24 (first additional batch)
    "long thick camshaft with small cams",
    "short thin camshaft with big cams",
    "long camshaft with wide journals",
    "short camshaft with narrow journals",
    "long thin camshaft",
    "short thick camshaft",
    "long thick camshaft with narrow journals",
    "short thin camshaft with wide journals",
    "long camshaft with big cams",
    "short camshaft with small cams",
    "thick camshaft with wide journals",
    "thin camshaft with narrow journals",
    "long thick camshaft",
    "short thin camshaft with big cams wide journals",
    "long thin camshaft with small cams",
    "short thick camshaft with narrow journals",
    "long camshaft with big cams wide journals",
    "short camshaft with small cams narrow journals",
    "long thick camshaft with big cams wide journals",
    "short thin camshaft with small cams narrow journals",
    "long thin camshaft with big cams narrow journals",
    "short thick camshaft with small cams wide journals",
    "long camshaft with small cams wide journals",
    "short camshaft with big cams narrow journals",
    "long thin camshaft with big cams narrow journals",
    "short thick camshaft with small cams wide journals",
    "long camshaft with small cams narrow journals",
    "short camshaft with big cams wide journals",
    "long thick camshaft with big cams",
    "short thin camshaft with small cams",
    "long camshaft with wide journals thin",
    "short camshaft with narrow journals thick",
    "long thick camshaft with small cams narrow journals",
    "short thin camshaft with big cams wide journals",
    "long thin camshaft with big cams",
    "short thick camshaft with small cams",
    "long camshaft with big cams narrow journals",
    "short camshaft with small cams wide journals",
    "long thick camshaft with wide journals",
    "short thin camshaft with narrow journals",
    "long thin camshaft with small cams wide journals",
    "short thick camshaft with big cams narrow journals",
    "long camshaft with thick big cams",
    "short camshaft with thin small cams"
]

metadata_list = []

# Generate metadata for all 50 camshafts
for idx, description in enumerate(descriptions):
    # Parse parameters
    params = parse_description(description)
    
    # Create filename matching existing STL files
    filename = f"camshaft_{idx}_{description.replace(' ', '_')}.stl"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Create labels
    labels = {
        "filename": filename,
        "description": description,
        "shaft_length": params["shaft_length"],
        "shaft_diameter": params["shaft_diameter"],
        "cam_major_diameter": params["cam_major_diameter"],
        "cam_minor_diameter": params["cam_minor_diameter"],
        "cam_thickness": params["cam_thickness"],
        "journal_diameter": params["journal_diameter"],
        "journal_thickness": params["journal_thickness"],
        "num_cams": params["num_cams"],
        "component_type": "camshaft"
    }
    
    # Store labels
    metadata_list.append(labels)
    
    print(f"Prepared metadata for: {filename}")

# Convert to DataFrame
metadata_df = pd.DataFrame(metadata_list)
print(f"Metadata DataFrame:\n{metadata_df}")

# Load and clean existing metadata.csv
if os.path.exists(METADATA_FILE):
    try:
        existing_df = pd.read_csv(METADATA_FILE, encoding='utf-8')
        print(f"Existing CSV before cleaning:\n{existing_df}")
        # Remove duplicates based on filename
        existing_df = existing_df.drop_duplicates(subset=['filename'], keep='first')
        print(f"Existing CSV after cleaning duplicates:\n{existing_df}")
    except Exception as e:
        print(f"Error reading {METADATA_FILE}: {e}. Starting with empty DataFrame.")
        existing_df = pd.DataFrame()
else:
    print(f"{METADATA_FILE} does not exist. Starting with empty DataFrame.")
    existing_df = pd.DataFrame()

# Combine DataFrames
if not existing_df.empty:
    combined_df = pd.concat([existing_df, metadata_df], ignore_index=True)
else:
    combined_df = metadata_df
print(f"Combined DataFrame:\n{combined_df}")

# Save to temporary file first, then move to target
try:
    # Write to temporary file
    combined_df.to_csv(TEMP_FILE, index=False, encoding='utf-8')
    print(f"Successfully wrote {len(combined_df)} rows to temporary file: {TEMP_FILE}")
    
    # Attempt to replace the target file
    shutil.move(TEMP_FILE, METADATA_FILE)
    print(f"Successfully moved temporary file to {METADATA_FILE}")
except PermissionError as e:
    print(f"Permission error: {e}")
    print(f"Could not write to {METADATA_FILE}. Steps to resolve:")
    print("1. Close any programs (e.g., Excel, VS Code) that may have metadata.csv open.")
    print("2. Run VS Code as Administrator: Right-click VS Code → Run as Administrator.")
    print("3. Disable OneDrive sync for the dataset folder: Right-click dataset folder → Pause syncing.")
    print(f"4. Check the temporary file at {TEMP_FILE} for the correct metadata.")
    print("5. Manually copy the temporary file to dataset/metadata.csv after resolving the issue.")
except Exception as e:
    print(f"Error writing to {METADATA_FILE}: {e}")
    print(f"Temporary file saved at {TEMP_FILE}. Manually copy it to {METADATA_FILE} after resolving the issue.")

# Verify the final CSV
try:
    final_df = pd.read_csv(METADATA_FILE, encoding='utf-8')
    print(f"Final CSV contains {len(final_df)} rows.")
    print(f"Camshaft entries: {len(final_df[final_df['component_type'] == 'camshaft'])}")
    print(f"Connecting rod entries: {len(final_df[final_df['component_type'] == 'connecting_rod'])}")
except Exception as e:
    print(f"Error verifying {METADATA_FILE}: {e}")
    print("Check if the file was updated correctly or use the temporary file.")