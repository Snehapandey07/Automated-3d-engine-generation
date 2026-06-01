import trimesh
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
import time
import psutil
import stat

# Set absolute paths
BASE_DIR = r"C:\Users\Sneha Pandey\OneDrive\Desktop\Automated 3d Model generation\Dataset\create dataset python"
METADATA_FILE = os.path.join(BASE_DIR, "dataset", "metadata.csv")
MODELS_DIR = os.path.join(BASE_DIR, "dataset", "models")
TEMP_FILE = os.path.join(tempfile.gettempdir(), "temp_metadata_crankcase.csv")

# Function to check if file is locked
def is_file_locked(filepath):
    try:
        with open(filepath, 'a'):
            return False
    except PermissionError:
        return True

# Function to force unlock file
def force_unlock_file(filepath):
    try:
        os.chmod(filepath, stat.S_IWRITE | stat.S_IREAD)
        print(f"Changed permissions for {filepath}")
    except Exception as e:
        print(f"Failed to change permissions for {filepath}: {e}")

# Function to parse description and set parameters
def parse_description(description):
    description = description.lower().strip()
    
    # Default values (in mm)
    params = {
        "cylinder_count": 4,
        "length": 500.0,
        "width": 300.0,
        "height": 200.0,
        "oil_pan_depth": 100.0,
        "bearing_diameter": 50.0,
        "flange_thickness": 15.0,
        "oil_pump_diameter": 40.0,
        "drain_plug_diameter": 20.0,
        "cooling_fins": False
    }
    
    # Keyword-based adjustments
    if "many" in description:
        params["cylinder_count"] = 6
    elif "few" in description:
        params["cylinder_count"] = 2
    
    if "long" in description:
        params["length"] = 600.0
    elif "short" in description:
        params["length"] = 400.0
    
    if "wide" in description:
        params["width"] = 350.0
    elif "narrow" in description:
        params["width"] = 250.0
    
    if "tall" in description:
        params["height"] = 250.0
    elif "short height" in description:
        params["height"] = 150.0
    
    if "deep oil pan" in description:
        params["oil_pan_depth"] = 120.0
    elif "shallow oil pan" in description:
        params["oil_pan_depth"] = 80.0
    
    if "large bearings" in description:
        params["bearing_diameter"] = 60.0
    elif "small bearings" in description:
        params["bearing_diameter"] = 40.0
    
    if "thick flanges" in description:
        params["flange_thickness"] = 20.0
    elif "thin flanges" in description:
        params["flange_thickness"] = 10.0
    
    if "high cooling" in description:
        params["cooling_fins"] = True
    
    # Geometric constraints
    min_length = params["cylinder_count"] * (params["bearing_diameter"] + 20) + 100
    if params["length"] < min_length:
        params["length"] = min_length
        print(f"Length adjusted to {params['length']} mm for {description}.")
    
    if params["height"] < params["oil_pan_depth"] + 50:
        params["height"] = params["oil_pan_depth"] + 50
        print(f"Height adjusted to {params['height']} mm for {description}.")
    
    return params

# Define 50 parameter combinations for crankcases
descriptions = [
    "long crankcase with many cylinders wide tall deep oil pan large bearings thick flanges high cooling",
    "short crankcase with few cylinders narrow short height shallow oil pan small bearings thin flanges",
    "crankcase with large bearings thick flanges high cooling",
    "crankcase with small bearings thin flanges",
    "long crankcase with few cylinders wide deep oil pan",
    "short crankcase with many cylinders narrow shallow oil pan",
    "tall crankcase with large bearings",
    "short height crankcase with small bearings",
    "crankcase with many cylinders wide high cooling",
    "crankcase with few cylinders narrow",
    "long crankcase with many cylinders thick flanges",
    "short crankcase with few cylinders thin flanges",
    "long crankcase with deep oil pan large bearings",
    "short crankcase with shallow oil pan small bearings",
    "crankcase with many cylinders tall high cooling",
    "crankcase with few cylinders short height",
    "long crankcase with narrow many cylinders",
    "short crankcase with wide few cylinders",
    "long crankcase with wide tall deep oil pan",
    "short crankcase with narrow short height shallow oil pan",
    "long crankcase with many cylinders shallow oil pan",
    "short crankcase with few cylinders deep oil pan",
    "crankcase with wide many cylinders large bearings high cooling",
    "crankcase with narrow few cylinders small bearings",
    "long crankcase with few cylinders thick flanges",
    "short crankcase with many cylinders thin flanges",
    "long crankcase with many cylinders wide tall large bearings high cooling",
    "short crankcase with few cylinders narrow short height small bearings",
    "tall crankcase with many cylinders high cooling",
    "short height crankcase with few cylinders",
    "long crankcase with shallow oil pan thick flanges",
    "short crankcase with deep oil pan thin flanges",
    "long crankcase with wide many cylinders",
    "short crankcase with narrow few cylinders",
    "long crankcase with many cylinders wide tall deep oil pan high cooling",
    "short crankcase with few cylinders narrow short height shallow oil pan",
    "long crankcase with shallow oil pan large bearings",
    "short crankcase with deep oil pan small bearings",
    "long crankcase with few cylinders wide tall high cooling",
    "short crankcase with many cylinders narrow short height",
    "long crankcase with many cylinders wide deep oil pan",
    "short crankcase with few cylinders narrow shallow oil pan",
    "tall crankcase with large bearings many cylinders",
    "short height crankcase with small bearings few cylinders",
    "long crankcase with wide tall large bearings high cooling",
    "short crankcase with narrow short height small bearings",
    "long crankcase with many cylinders shallow oil pan thick flanges",
    "short crankcase with few cylinders deep oil pan thin flanges",
    "long crankcase with many cylinders wide high cooling",
    "short crankcase with few cylinders narrow"
]

# Initialize metadata list
metadata_list = []

# Generate STL files and labels
for idx, description in enumerate(descriptions):
    # Parse parameters
    params = parse_description(description)
    
    # Create filename
    filename = f"crankcase_{idx}_{description.replace(' ', '_')}.stl"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Skip if STL already exists
    if os.path.exists(filepath):
        print(f"STL exists, skipping generation: {filepath}")
    else:
        # Create main housing
        main_housing = trimesh.creation.box(
            extents=[params["length"], params["width"], params["height"]]
        )
        main_housing.apply_translation([0, 0, params["height"]/2])
        
        # Initialize scene
        crankcase = main_housing
        
        # Calculate bearing support positions
        bearing_spacing = params["length"] / (params["cylinder_count"] + 1)
        bearing_positions = [bearing_spacing * (i + 1) - params["length"]/2 for i in range(params["cylinder_count"])]
        
        # Create bearing supports
        for x_pos in bearing_positions:
            bearing_support = trimesh.creation.cylinder(
                radius=params["bearing_diameter"]/2,
                height=params["width"],
                segments=50
            )
            bearing_support.apply_transform(trimesh.transformations.rotation_matrix(
                angle=np.radians(90), direction=[0, 1, 0]
            ))
            bearing_support.apply_translation([x_pos, 0, params["height"]/2])
            crankcase = crankcase.difference(bearing_support)
        
        # Create oil pan
        oil_pan = trimesh.creation.box(
            extents=[params["length"] * 0.8, params["width"] * 0.9, params["oil_pan_depth"]]
        )
        oil_pan.apply_translation([0, 0, -params["oil_pan_depth"]/2])
        crankcase = trimesh.util.concatenate([crankcase, oil_pan])
        
        # Create mounting flanges (4: two on each side)
        flange_x_positions = [-params["length"]/2, params["length"]/2]
        for x_pos in flange_x_positions:
            for y_offset in [-params["width"]/2, params["width"]/2]:
                flange = trimesh.creation.box(
                    extents=[params["flange_thickness"], 50.0, params["height"]]
                )
                flange.apply_translation([x_pos, y_offset, params["height"]/2])
                crankcase = trimesh.util.concatenate([crankcase, flange])
        
        # Create oil pump housing
        oil_pump = trimesh.creation.cylinder(
            radius=params["oil_pump_diameter"]/2,
            height=30.0,
            segments=50
        )
        oil_pump.apply_translation([params["length"]/2 - 50, 0, -params["oil_pan_depth"]/2])
        crankcase = crankcase.difference(oil_pump)
        
        # Create drain plug hole
        drain_plug = trimesh.creation.cylinder(
            radius=params["drain_plug_diameter"]/2,
            height=20.0,
            segments=50
        )
        drain_plug.apply_translation([0, 0, -params["oil_pan_depth"]/2])
        crankcase = crankcase.difference(drain_plug)
        
        # Add cooling fins (if enabled)
        if params["cooling_fins"]:
            fin_count = 5
            fin_spacing = params["length"] * 0.8 / (fin_count + 1)
            for i in range(fin_count):
                fin = trimesh.creation.box(
                    extents=[10.0, params["width"] * 0.9, params["oil_pan_depth"] * 0.8]
                )
                fin.apply_translation([(i + 1) * fin_spacing - params["length"] * 0.4, 0, -params["oil_pan_depth"]/2])
                crankcase = trimesh.util.concatenate([crankcase, fin])
        
        # Export as STL
        try:
            crankcase.export(filepath)
            print(f"Generated: {filepath}")
        except Exception as e:
            print(f"Error exporting {filepath}: {e}")
    
    # Create labels
    labels = {
        "filename": filename,
        "description": description,
        "cylinder_count": params["cylinder_count"],
        "length": params["length"],
        "width": params["width"],
        "height": params["height"],
        "oil_pan_depth": params["oil_pan_depth"],
        "bearing_diameter": params["bearing_diameter"],
        "flange_thickness": params["flange_thickness"],
        "component_type": "crankcase"
    }
    
    # Store labels
    metadata_list.append(labels)

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

# Verify DataFrame integrity
if len(combined_df) != 250:
    print(f"Warning: Combined DataFrame has {len(combined_df)} rows, expected 250.")
print(f"Combined DataFrame counts:")
print(f"Camshafts: {len(combined_df[combined_df['component_type'] == 'camshaft'])}")
print(f"Connecting rods: {len(combined_df[combined_df['component_type'] == 'connecting_rod'])}")
print(f"Crankshafts: {len(combined_df[combined_df['component_type'] == 'crankshaft'])}")
print(f"Cylinder heads: {len(combined_df[combined_df['component_type'] == 'cylinder_head'])}")
print(f"Crankcases: {len(combined_df[combined_df['component_type'] == 'crankcase'])}")

# Save to temporary file with retry mechanism
max_retries = 5
retry_delay = 5  # seconds
for attempt in range(max_retries):
    try:
        # Check if metadata.csv is locked
        if os.path.exists(METADATA_FILE) and is_file_locked(METADATA_FILE):
            print(f"Warning: {METADATA_FILE} is locked by another process.")
            print("Ensure Excel or other programs are not accessing metadata.csv.")
            force_unlock_file(METADATA_FILE)
        
        # Write to temporary file with UTF-8-SIG
        combined_df.to_csv(TEMP_FILE, index=False, encoding='utf-8-sig')
        print(f"Successfully wrote {len(combined_df)} rows to temporary file: {TEMP_FILE}")
        
        # Verify temporary file
        temp_df = pd.read_csv(TEMP_FILE, encoding='utf-8')
        if len(temp_df) != len(combined_df):
            raise Exception(f"Temporary file has {len(temp_df)} rows, expected {len(combined_df)}.")
        
        # Attempt to replace the target file
        shutil.move(TEMP_FILE, METADATA_FILE)
        print(f"Successfully moved temporary file to {METADATA_FILE}")
        break
    except PermissionError as e:
        print(f"Attempt {attempt + 1}/{max_retries} - Permission error: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"Could not write to {METADATA_FILE} after {max_retries} attempts. Steps to resolve:")
            print("1. Close any programs (e.g., Excel, VS Code) accessing metadata.csv.")
            print("2. Run VS Code as Administrator: Right-click VS Code → Run as Administrator.")
            print("3. Disable OneDrive sync: Right-click dataset folder → Pause syncing.")
            print(f"4. Check the temporary file at {TEMP_FILE} for the correct metadata.")
            print("5. Manually copy the temporary file to dataset/metadata.csv after resolving the issue.")
            print("6. Verify file permissions: Right-click metadata.csv → Properties → Security → Ensure 'Full control'.")
    except Exception as e:
        print(f"Attempt {attempt + 1}/{max_retries} - Error writing to {METADATA_FILE}: {e}")
        print(f"Temporary file saved at {TEMP_FILE}. Manually copy it to {METADATA_FILE} after resolving the issue.")
        break

# Verify the final CSV
try:
    final_df = pd.read_csv(METADATA_FILE, encoding='utf-8')
    print(f"Final CSV contains {len(final_df)} rows.")
    print(f"Camshaft entries: {len(final_df[final_df['component_type'] == 'camshaft'])}")
    print(f"Connecting rod entries: {len(final_df[final_df['component_type'] == 'connecting_rod'])}")
    print(f"Crankshaft entries: {len(final_df[final_df['component_type'] == 'crankshaft'])}")
    print(f"Cylinder head entries: {len(final_df[final_df['component_type'] == 'cylinder_head'])}")
    print(f"Crankcase entries: {len(final_df[final_df['component_type'] == 'crankcase'])}")
except Exception as e:
    print(f"Error verifying {METADATA_FILE}: {e}")
    print("Check if the file was updated correctly or use the temporary file.")