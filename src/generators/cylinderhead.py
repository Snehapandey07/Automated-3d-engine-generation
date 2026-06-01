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
TEMP_FILE = os.path.join(tempfile.gettempdir(), "temp_metadata_cylinder_head.csv")

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
        "head_length": 400.0,
        "head_width": 150.0,
        "head_height": 120.0,
        "port_diameter": 25.0,
        "valve_diameter": 30.0,
        "bolt_diameter": 10.0,
        "cooling_diameter": 15.0,
        "spring_height": 20.0,
        "rocker_shaft_diameter": 15.0,
        "thermostat_diameter": 30.0
    }
    
    # Keyword-based adjustments
    if "many" in description:
        params["cylinder_count"] = 6
    elif "few" in description:
        params["cylinder_count"] = 2
        
    if "long" in description:
        params["head_length"] = 500.0
    elif "short" in description:
        params["head_length"] = 300.0
        
    if "large ports" in description:
        params["port_diameter"] = 30.0
    elif "small ports" in description:
        params["port_diameter"] = 20.0
        
    if "large valves" in description:
        params["valve_diameter"] = 35.0
    elif "small valves" in description:
        params["valve_diameter"] = 25.0
    
    # Geometric constraints
    min_head_length = params["cylinder_count"] * (params["valve_diameter"] + 20) + 60
    if params["head_length"] < min_head_length:
        params["head_length"] = min_head_length
        print(f"Head length adjusted to {params['head_length']} mm for {description}.")
    
    if params["valve_diameter"] <= params["port_diameter"]:
        params["valve_diameter"] = params["port_diameter"] + 5.0
        print(f"Valve diameter adjusted to {params['valve_diameter']} mm.")
    
    return params

# Define 50 parameter combinations for cylinder heads
descriptions = [
    "long cylinder head with many cylinders large ports large valves",
    "short cylinder head with few cylinders small ports small valves",
    "cylinder head with large ports large valves",
    "cylinder head with small ports small valves",
    "long cylinder head with few cylinders large ports",
    "short cylinder head with many cylinders small ports",
    "long cylinder head with large valves",
    "short cylinder head with small valves",
    "cylinder head with many cylinders large ports",
    "cylinder head with few cylinders small ports",
    "long cylinder head with many cylinders large valves",
    "short cylinder head with few cylinders small valves",
    "long cylinder head with large ports small valves",
    "short cylinder head with small ports large valves",
    "cylinder head with many cylinders large valves",
    "cylinder head with few cylinders small valves",
    "long cylinder head with small ports many cylinders",
    "short cylinder head with large ports few cylinders",
    "long cylinder head with large ports large valves",
    "short cylinder head with small ports small valves",
    "long cylinder head with many cylinders small ports",
    "short cylinder head with few cylinders large ports",
    "cylinder head with large ports many cylinders large valves",
    "cylinder head with small ports few cylinders small valves",
    "long cylinder head with few cylinders large valves",
    "short cylinder head with many cylinders small valves",
    "long cylinder head with many cylinders large ports large valves",
    "short cylinder head with few cylinders small ports small valves",
    "long cylinder head with many cylinders large valves",
    "short cylinder head with few cylinders small valves",
    "long cylinder head with small ports large valves",
    "short cylinder head with large ports small valves",
    "long cylinder head with large ports many cylinders",
    "short cylinder head with small ports few cylinders",
    "long cylinder head with many cylinders large ports large valves",
    "short cylinder head with few cylinders small ports small valves",
    "long cylinder head with small ports large valves",
    "short cylinder head with large ports small valves",
    "long cylinder head with few cylinders large ports large valves",
    "short cylinder head with many cylinders small ports small valves",
    "long cylinder head with many cylinders large ports small valves",
    "short cylinder head with few cylinders small ports large valves",
    "long cylinder head with large valves many cylinders",
    "short cylinder head with small valves few cylinders",
    "long cylinder head with large ports large valves many cylinders",
    "short cylinder head with small ports small valves few cylinders",
    "long cylinder head with many cylinders small ports large valves",
    "short cylinder head with few cylinders large ports small valves",
    "long cylinder head with many cylinders large ports",
    "short cylinder head with few cylinders small ports"
]

# Initialize metadata list
metadata_list = []

# Generate labels (skip STL generation)
for idx, description in enumerate(descriptions):
    # Parse parameters
    params = parse_description(description)
    
    # Create filename
    filename = f"cylinder_head_{idx}_{description.replace(' ', '_')}.stl"
    filepath = os.path.join(MODELS_DIR, filename)
    
    # Verify STL exists
    if not os.path.exists(filepath):
        print(f"Warning: STL missing: {filepath}")
    
    # Create labels
    labels = {
        "filename": filename,
        "description": description,
        "cylinder_count": params["cylinder_count"],
        "head_length": params["head_length"],
        "port_diameter": params["port_diameter"],
        "valve_diameter": params["valve_diameter"],
        "component_type": "cylinder_head"
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
if len(combined_df) != 200:
    print(f"Warning: Combined DataFrame has {len(combined_df)} rows, expected 200.")
print(f"Combined DataFrame counts:")
print(f"Camshafts: {len(combined_df[combined_df['component_type'] == 'camshaft'])}")
print(f"Connecting rods: {len(combined_df[combined_df['component_type'] == 'connecting_rod'])}")
print(f"Crankshafts: {len(combined_df[combined_df['component_type'] == 'crankshaft'])}")
print(f"Cylinder heads: {len(combined_df[combined_df['component_type'] == 'cylinder_head'])}")

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
except Exception as e:
    print(f"Error verifying {METADATA_FILE}: {e}")
    print("Check if the file was updated correctly or use the temporary file.")