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
TEMP_FILE = os.path.join(tempfile.gettempdir(), "temp_metadata_crankshaft.csv")

# Function to parse description and set parameters
def parse_description(description):
    description = description.lower().strip()
    
    # Default values (in mm)
    params = {
        "shaft_length": 450.0,
        "shaft_diameter": 30.0,
        "throw_count": 4,
        "web_thickness": 15.0,
        "counterweight_radius": 50.0,
        "throw_offset": 40.0,
        "throw_diameter": 25.0
    }
    
    # Keyword-based adjustments
    if "long" in description:
        params["shaft_length"] = 600.0
    elif "short" in description:
        params["shaft_length"] = 300.0
        
    if "many" in description:
        params["throw_count"] = 6
    elif "few" in description:
        params["throw_count"] = 2
        
    if "thick" in description:
        params["web_thickness"] = 20.0
    elif "thin" in description:
        params["web_thickness"] = 10.0
        
    if "large" in description:
        params["counterweight_radius"] = 60.0
    elif "small" in description:
        params["counterweight_radius"] = 40.0
    
    # Geometric constraints
    min_shaft_length = (params["throw_count"] * 2 + 1) * params["web_thickness"] + 50
    if params["shaft_length"] < min_shaft_length:
        params["shaft_length"] = min_shaft_length
        print(f"Shaft length adjusted to {params['shaft_length']} mm for {description}.")
    
    if params["counterweight_radius"] <= params["shaft_diameter"]/2:
        params["counterweight_radius"] = params["shaft_diameter"]/2 + 10.0
        print(f"Counterweight radius adjusted to {params['counterweight_radius']} mm.")
    
    return params

# Define 50 parameter combinations for crankshafts
descriptions = [
    "long crankshaft with many throws thick webs large counterweights",
    "short crankshaft with few throws thin webs small counterweights",
    "crankshaft with thick webs large counterweights",
    "crankshaft with thin webs small counterweights",
    "long crankshaft with few throws thick webs",
    "short crankshaft with many throws thin webs",
    "long crankshaft with large counterweights",
    "short crankshaft with small counterweights",
    "crankshaft with many throws thick webs",
    "crankshaft with few throws thin webs",
    "long thick crankshaft with many throws",
    "short thin crankshaft with few throws",
    "long crankshaft with thick webs small counterweights",
    "short crankshaft with thin webs large counterweights",
    "crankshaft with many throws large counterweights",
    "crankshaft with few throws small counterweights",
    "long crankshaft with thin webs many throws",
    "short crankshaft with thick webs few throws",
    "long thick crankshaft with large counterweights",
    "short thin crankshaft with small counterweights",
    "long crankshaft with many throws thin webs",
    "short crankshaft with few throws thick webs",
    "crankshaft with thick webs many throws large counterweights",
    "crankshaft with thin webs few throws small counterweights",
    "long thick crankshaft with few throws large counterweights",
    "short thin crankshaft with many throws small counterweights",
    "long crankshaft with thick webs many throws large counterweights",
    "short crankshaft with thin webs few throws small counterweights",
    "long crankshaft with many throws large counterweights",
    "short crankshaft with few throws small counterweights",
    "long thick crankshaft with thin webs many throws",
    "short thin crankshaft with thick webs few throws",
    "long crankshaft with large counterweights many throws",
    "short crankshaft with small counterweights few throws",
    "long thick crankshaft with many throws large counterweights",
    "short thin crankshaft with few throws small counterweights",
    "long crankshaft with thin webs large counterweights",
    "short crankshaft with thick webs small counterweights",
    "long thick crankshaft with few throws thin webs",
    "short thin crankshaft with many throws thick webs",
    "long crankshaft with many throws thick webs small counterweights",
    "short crankshaft with few throws thin webs large counterweights",
    "long thick crankshaft with large counterweights few throws",
    "short thin crankshaft with small counterweights many throws",
    "long crankshaft with thick webs large counterweights many throws",
    "short crankshaft with thin webs small counterweights few throws",
    "long thick crankshaft with many throws thin webs large counterweights",
    "short thin crankshaft with few throws thick webs small counterweights",
    "long crankshaft with many throws thick webs",
    "short crankshaft with few throws thin webs"
]

# Initialize metadata list
metadata_list = []

# Generate STL files and labels
for idx, description in enumerate(descriptions):
    # Parse parameters
    params = parse_description(description)
    
    # Create filename
    filename = f"crankshaft_{idx}_{description.replace(' ', '_')}.stl"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Create main shaft
    main_shaft = trimesh.creation.cylinder(
        radius=params["shaft_diameter"]/2,
        height=params["shaft_length"],
        segments=100
    )
    main_shaft.apply_translation([0, 0, params["shaft_length"]/2])
    
    # Initialize scene
    crankshaft = main_shaft
    
    # Calculate spacing for throws
    segment_length = params["shaft_length"] / (params["throw_count"] * 2 + 1)
    throw_positions = [segment_length * (i * 2 + 1) for i in range(params["throw_count"])]
    
    # Create throws, webs, and counterweights
    for i, z_pos in enumerate(throw_positions):
        # Web before throw
        web_before = trimesh.creation.box(
            extents=[params["counterweight_radius"]*2, params["web_thickness"], params["web_thickness"]]
        )
        web_before.apply_translation([params["throw_offset"]/2, 0, z_pos - params["web_thickness"]/2])
        
        # Throw (crankpin)
        throw = trimesh.creation.cylinder(
            radius=params["throw_diameter"]/2,
            height=params["web_thickness"],
            segments=100
        )
        throw.apply_translation([params["throw_offset"], 0, z_pos])
        
        # Web after throw
        web_after = trimesh.creation.box(
            extents=[params["counterweight_radius"]*2, params["web_thickness"], params["web_thickness"]]
        )
        web_after.apply_translation([params["throw_offset"]/2, 0, z_pos + params["web_thickness"]/2])
        
        # Counterweight (semicircular)
        counterweight = trimesh.creation.annulus(
            r_min=params["shaft_diameter"]/2,
            r_max=params["counterweight_radius"],
            height=params["web_thickness"],
            segments=100
        )
        counterweight.apply_translation([-params["throw_offset"]/2, 0, z_pos])
        
        # Rotate for multi-throw crankshafts
        angle = (i * 180.0) % 360.0  # Alternate throws for balance
        for component in [web_before, throw, web_after, counterweight]:
            component.apply_transform(trimesh.transformations.rotation_matrix(
                angle=np.radians(angle),
                direction=[0, 0, 1],
                point=[0, 0, z_pos]
            ))
        
        # Add to crankshaft
        crankshaft = trimesh.util.concatenate([crankshaft, web_before, throw, web_after, counterweight])
    
    # Export as STL
    crankshaft.export(filepath)
    
    # Create labels
    labels = {
        "filename": filename,
        "description": description,
        "shaft_length": params["shaft_length"],
        "throw_count": params["throw_count"],
        "web_thickness": params["web_thickness"],
        "counterweight_radius": params["counterweight_radius"],
        "component_type": "crankshaft"
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
    # Write to temporary file with UTF-8 encoding
    combined_df.to_csv(TEMP_FILE, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
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
    print(f"Crankshaft entries: {len(final_df[final_df['component_type'] == 'crankshaft'])}")
except Exception as e:
    print(f"Error verifying {METADATA_FILE}: {e}")
    print("Check if the file was updated correctly or use the temporary file.")