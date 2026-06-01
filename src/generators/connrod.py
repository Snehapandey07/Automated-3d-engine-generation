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
TEMP_FILE = os.path.join(tempfile.gettempdir(), "temp_metadata_connrod.csv")

# Function to parse description and set parameters
def parse_description(description):
    description = description.lower().strip()
    
    # Default values (in mm)
    params = {
        "rod_length": 150.0,
        "big_end_diameter": 50.0,
        "small_end_diameter": 25.0,
        "shaft_thickness": 15.0,
        "rod_thickness": 10.0
    }
    
    # Keyword-based adjustments
    if "long" in description:
        params["rod_length"] = 200.0
    elif "short" in description:
        params["rod_length"] = 100.0
        
    if "big" in description:
        params["big_end_diameter"] = 60.0
        params["small_end_diameter"] = 30.0
    elif "small" in description:
        params["big_end_diameter"] = 40.0
        params["small_end_diameter"] = 20.0
        
    if "thick" in description:
        params["shaft_thickness"] = 20.0
        params["rod_thickness"] = 15.0
    elif "thin" in description:
        params["shaft_thickness"] = 10.0
        params["rod_thickness"] = 8.0
        
    if "wide" in description:
        params["shaft_thickness"] += 5.0
    elif "narrow" in description:
        params["shaft_thickness"] -= 5.0
    
    # Geometric constraints
    if params["big_end_diameter"] <= params["small_end_diameter"]:
        params["big_end_diameter"] = params["small_end_diameter"] + 10.0
        print(f"Big end diameter adjusted to {params['big_end_diameter']} mm.")
    
    if params["shaft_thickness"] < 5.0:
        params["shaft_thickness"] = 5.0
        print(f"Shaft thickness adjusted to {params['shaft_thickness']} mm.")
    
    if params["rod_length"] < (params["big_end_diameter"] + params["small_end_diameter"] + 20):
        params["rod_length"] = params["big_end_diameter"] + params["small_end_diameter"] + 20
        print(f"Rod length adjusted to {params['rod_length']} mm.")
    
    return params

# Define 44 new parameter combinations
descriptions = [
    "long thick rod with small end narrow shaft",
    "short thin rod with big end wide shaft",
    "long rod with big end narrow shaft",
    "short rod with small end wide shaft",
    "long thick rod with big end",
    "short thin rod with small end",
    "long rod with wide shaft thick",
    "short rod with narrow shaft thin",
    "long thick rod with small end wide shaft",
    "short thin rod with big end narrow shaft",
    "long thin rod with big end",
    "short thick rod with small end",
    "long rod with big end wide shaft",
    "short rod with small end narrow shaft",
    "long thick rod with wide shaft",
    "short thin rod with narrow shaft",
    "long thin rod with small end wide shaft",
    "short thick rod with big end narrow shaft",
    "long rod with thick big end",
    "short rod with thin small end",
    "long thick rod with big end wide shaft",
    "short thin rod with small end narrow shaft",
    "long thin rod with big end narrow shaft",
    "short thick rod with small end wide shaft",
    "long rod with small end narrow shaft",
    "short rod with big end wide shaft",
    "long thick rod with small end",
    "short thin rod with big end",
    "long rod with wide shaft thin",
    "short rod with narrow shaft thick",
    "long thick rod with big end narrow shaft",
    "short thin rod with small end wide shaft",
    "long thin rod with big end wide shaft",
    "short thick rod with small end narrow shaft",
    "long rod with big end narrow shaft",
    "short rod with small end wide shaft",
    "long thick rod with wide shaft thin",
    "short thin rod with narrow shaft thick",
    "long thin rod with small end narrow shaft",
    "short thick rod with big end wide shaft",
    "long rod with thick big end wide shaft",
    "short rod with thin small end narrow shaft",
    "long thick rod with big end narrow shaft",
    "short thin rod with small end wide shaft"
]

# Initialize metadata list
metadata_list = []

# Start index at 6 to continue from existing connecting rods
start_index = 6

# Generate STL files and labels
for idx, description in enumerate(descriptions):
    # Use incremental index
    current_index = start_index + idx
    
    # Parse parameters
    params = parse_description(description)
    
    # Create unique filename
    filename = f"connecting_rod_{current_index}_{description.replace(' ', '_')}.stl"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Create Big End
    big_end = trimesh.creation.annulus(
        r_min=params["big_end_diameter"]/2 - params["rod_thickness"],
        r_max=params["big_end_diameter"]/2,
        height=params["rod_thickness"],
        segments=100
    )
    big_end.apply_translation([0, 0, params["rod_thickness"]/2])
    
    # Create Small End
    small_end = trimesh.creation.annulus(
        r_min=params["small_end_diameter"]/2 - params["rod_thickness"],
        r_max=params["small_end_diameter"]/2,
        height=params["rod_thickness"],
        segments=100
    )
    small_end.apply_translation([0, 0, params["rod_length"] - params["rod_thickness"]/2])
    
    # Create Shaft
    shaft_length = params["rod_length"] - params["big_end_diameter"]/2 - params["small_end_diameter"]/2
    shaft = trimesh.creation.box(
        extents=[params["shaft_thickness"], params["shaft_thickness"], shaft_length]
    )
    shaft.apply_translation([0, 0, params["big_end_diameter"]/2 + shaft_length/2])
    
    # Combine into one model
    connecting_rod = trimesh.util.concatenate([big_end, small_end, shaft])
    
    # Export as STL
    connecting_rod.export(filepath)
    
    # Create labels
    labels = {
        "filename": filename,
        "description": description,
        "rod_length": params["rod_length"],
        "big_end_diameter": params["big_end_diameter"],
        "small_end_diameter": params["small_end_diameter"],
        "shaft_thickness": params["shaft_thickness"],
        "rod_thickness": params["rod_thickness"],
        "component_type": "connecting_rod"
    }
    
    # Store labels
    metadata_list.append(labels)
    
    print(f"Generated: {filepath}")

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