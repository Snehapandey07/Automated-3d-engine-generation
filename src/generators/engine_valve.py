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
TEMP_FILE = os.path.join(tempfile.gettempdir(), "temp_metadata_engine_valve.csv")

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
        "valve_type": "intake",
        "stem_length": 100.0,
        "stem_diameter": 6.0,
        "head_diameter": 30.0,
        "head_thickness": 4.0,
        "filleted": False
    }
    
    # Keyword-based adjustments
    if "exhaust" in description:
        params["valve_type"] = "exhaust"
        params["head_diameter"] = 25.0  # Smaller head for exhaust
    if "long stem" in description:
        params["stem_length"] = 120.0
    elif "short stem" in description:
        params["stem_length"] = 80.0
    if "large head" in description:
        params["head_diameter"] = 35.0 if params["valve_type"] == "intake" else 30.0
    elif "small head" in description:
        params["head_diameter"] = 25.0 if params["valve_type"] == "intake" else 20.0
    if "thick stem" in description:
        params["stem_diameter"] = 8.0
    elif "thin stem" in description:
        params["stem_diameter"] = 5.0
    if "filleted" in description:
        params["filleted"] = True
    
    # Geometric constraints
    if params["head_diameter"] < params["stem_diameter"] * 3:
        params["head_diameter"] = params["stem_diameter"] * 3
        print(f"Head diameter adjusted to {params['head_diameter']} mm for {description}.")
    
    if params["head_thickness"] > params["head_diameter"] / 4:
        params["head_thickness"] = params["head_diameter"] / 4
        print(f"Head thickness adjusted to {params['head_thickness']} mm for {description}.")
    
    return params

# Define 50 parameter combinations for engine valves
descriptions = [
    "intake valve with long stem large head thick stem filleted",
    "exhaust valve with short stem small head thin stem",
    "intake valve with large head filleted",
    "exhaust valve with small head",
    "intake valve with long stem thick stem",
    "exhaust valve with short stem thin stem",
    "intake valve with large head thick stem filleted",
    "exhaust valve with small head thin stem",
    "intake valve with long stem large head",
    "exhaust valve with short stem small head",
    "intake valve with thick stem filleted",
    "exhaust valve with thin stem",
    "intake valve with long stem small head filleted",
    "exhaust valve with short stem large head",
    "intake valve with large head thin stem",
    "exhaust valve with small head thick stem",
    "intake valve with long stem filleted",
    "exhaust valve with short stem",
    "intake valve with large head thick stem",
    "exhaust valve with small head thin stem filleted",
    "intake valve with long stem large head filleted",
    "exhaust valve with short stem small head",
    "intake valve with thick stem large head",
    "exhaust valve with thin stem small head",
    "intake valve with long stem thin stem filleted",
    "exhaust valve with short stem thick stem",
    "intake valve with large head filleted",
    "exhaust valve with small head thin stem",
    "intake valve with long stem thick stem large head",
    "exhaust valve with short stem small head thin stem",
    "intake valve with filleted thick stem",
    "exhaust valve with thin stem",
    "intake valve with long stem large head thin stem",
    "exhaust valve with short stem small head thick stem",
    "intake valve with large head thick stem filleted",
    "exhaust valve with small head thin stem",
    "intake valve with long stem small head",
    "exhaust valve with short stem large head filleted",
    "intake valve with thick stem large head",
    "exhaust valve with thin stem small head filleted",
    "intake valve with long stem thick stem filleted",
    "exhaust valve with short stem thin stem",
    "intake valve with large head thin stem filleted",
    "exhaust valve with small head thick stem",
    "intake valve with long stem large head thick stem",
    "exhaust valve with short stem small head thin stem",
    "intake valve with filleted large head",
    "exhaust valve with thin stem short stem",
    "intake valve with long stem thick stem filleted",
    "exhaust valve with small head thin stem"
]

# Initialize metadata list
metadata_list = []

# Generate STL files and labels
for idx, description in enumerate(descriptions):
    # Parse parameters
    params = parse_description(description)
    
    # Create filename
    filename = f"engine_valve_{idx}_{description.replace(' ', '_')}.stl"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Skip if STL already exists
    if os.path.exists(filepath):
        print(f"STL exists, skipping generation: {filepath}")
    else:
        # Create valve stem
        stem = trimesh.creation.cylinder(
            radius=params["stem_diameter"]/2,
            height=params["stem_length"],
            segments=50
        )
        stem.apply_translation([0, 0, params["stem_length"]/2])
        
        # Create valve head
        head = trimesh.creation.cylinder(
            radius=params["head_diameter"]/2,
            height=params["head_thickness"],
            segments=50
        )
        head.apply_translation([0, 0, params["stem_length"]])
        
        # Create keeper groove (near stem tip)
        groove = trimesh.creation.cylinder(
            radius=params["stem_diameter"]/2 - 0.5,  # Slightly smaller
            height=2.0,
            segments=50
        )
        groove.apply_translation([0, 0, params["stem_length"] - 5.0])
        valve = stem.union(head).difference(groove)
        
        # Add fillet (approximated as a single-radius cone)
        if params["filleted"]:
            fillet_radius = (params["head_diameter"]/2 + params["stem_diameter"]/2) / 2  # Average radius
            fillet = trimesh.creation.cone(
                radius=fillet_radius,
                height=5.0,
                segments=50
            )
            fillet.apply_translation([0, 0, params["stem_length"] - 2.5])
            valve = valve.union(fillet)
        
        # Export as STL
        try:
            valve.export(filepath)
            print(f"Generated: {filepath}")
        except Exception as e:
            print(f"Error exporting {filepath}: {e}")
    
    # Create labels
    labels = {
        "filename": filename,
        "description": description,
        "valve_type": params["valve_type"],
        "stem_length": params["stem_length"],
        "stem_diameter": params["stem_diameter"],
        "head_diameter": params["head_diameter"],
        "head_thickness": params["head_thickness"],
        "filleted": params["filleted"],
        "component_type": "engine_valve"
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
if len(combined_df) != 300:
    print(f"Warning: Combined DataFrame has {len(combined_df)} rows, expected 300.")
print(f"Combined DataFrame counts:")
print(f"Camshafts: {len(combined_df[combined_df['component_type'] == 'camshaft'])}")
print(f"Connecting rods: {len(combined_df[combined_df['component_type'] == 'connecting_rod'])}")
print(f"Crankshafts: {len(combined_df[combined_df['component_type'] == 'crankshaft'])}")
print(f"Cylinder heads: {len(combined_df[combined_df['component_type'] == 'cylinder_head'])}")
print(f"Crankcases: {len(combined_df[combined_df['component_type'] == 'crankcase'])}")
print(f"Engine valves: {len(combined_df[combined_df['component_type'] == 'engine_valve'])}")

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
    print(f"Engine valve entries: {len(final_df[final_df['component_type'] == 'engine_valve'])}")
except Exception as e:
    print(f"Error verifying {METADATA_FILE}: {e}")
    print("Check if the file was updated correctly or use the temporary file.")