import pandas as pd
import os

# Set paths
BASE_DIR = r"C:\Users\Sneha Pandey\Desktop\Automated 3d Model generation\Dataset\create dataset python"
MODEL_DIR = os.path.join(BASE_DIR, "dataset", "models")
METADATA_FILE = os.path.join(BASE_DIR, "dataset", "metadata.csv")

# Load metadata
metadata = pd.read_csv(METADATA_FILE)

# Filter out NaN component types
metadata = metadata[metadata['component_type'].notna()]

# Filter out entries for missing files
valid_entries = []
missing_files = []
for idx, row in metadata.iterrows():
    filename = row['filename']
    file_path = os.path.join(MODEL_DIR, filename)
    if os.path.exists(file_path):
        valid_entries.append(row)
    else:
        missing_files.append(filename)

# Create new DataFrame with valid entries
cleaned_metadata = pd.DataFrame(valid_entries)

# Save the updated metadata
cleaned_metadata.to_csv(METADATA_FILE, index=False, encoding="utf-8-sig")

# Print results
print(f"Removed {len(missing_files)} entries for missing files.")
print("Missing files:", missing_files)
print(f"Updated metadata saved to {METADATA_FILE}")
print(f"New dataset size: {len(cleaned_metadata)} entries")