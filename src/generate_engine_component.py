import trimesh
import numpy as np
import os
import re

# path
BASE_DIR = r"C:\Users\Sneha Pandey\OneDrive\Desktop\Automated 3d Model generation\Dataset\create dataset python"
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset", "outputs")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Supported components
COMPONENTS = [
    "camshaft", "connecting_rod", "crankshaft", 
    "cylinder_head", "crankcase", "engine_valve"
]

# Parameter parsing functions
def parse_camshaft(description):
    description = description.lower().strip()
    params = {
        "length": 500.0,
        "diameter": 25.0,
        "lobe_count": 8,
        "lobe_height": 10.0
    }
    if "long" in description:
        params["length"] = 600.0
    elif "short" in description:
        params["length"] = 400.0
    if "many lobes" in description:
        params["lobe_count"] = 12
    elif "few lobes" in description:
        params["lobe_count"] = 4
    if "large lobes" in description:
        params["lobe_height"] = 15.0
    elif "small lobes" in description:
        params["lobe_height"] = 5.0
    return params

def parse_connecting_rod(description):
    description = description.lower().strip()
    params = {
        "length": 150.0,
        "big_end_diameter": 50.0,
        "small_end_diameter": 25.0,
        "thickness": 15.0
    }
    if "long" in description:
        params["length"] = 200.0
    elif "short" in description:
        params["length"] = 100.0
    if "large big end" in description:
        params["big_end_diameter"] = 60.0
    elif "small big end" in description:
        params["big_end_diameter"] = 40.0
    if "large small end" in description:
        params["small_end_diameter"] = 30.0
    elif "small small end" in description:
        params["small_end_diameter"] = 20.0
    return params

def parse_crankshaft(description):
    description = description.lower().strip()
    params = {
        "length": 600.0,
        "journal_diameter": 50.0,
        "throw_count": 4,
        "throw_length": 40.0
    }
    if "long" in description:
        params["length"] = 800.0
    elif "short" in description:
        params["length"] = 400.0
    if "many throws" in description:
        params["throw_count"] = 6
    elif "few throws" in description:
        params["throw_count"] = 2
    if "large throws" in description:
        params["throw_length"] = 50.0
    elif "small throws" in description:
        params["throw_length"] = 30.0
    return params

def parse_cylinder_head(description):
    description = description.lower().strip()
    params = {
        "length": 400.0,
        "width": 200.0,
        "height": 100.0,
        "valve_count": 4,
        "cooling_fins": False
    }
    if "large" in description:
        params["length"], params["width"], params["height"] = 500.0, 250.0, 120.0
    elif "small" in description:
        params["length"], params["width"], params["height"] = 300.0, 150.0, 80.0
    if "many valves" in description:
        params["valve_count"] = 8
    elif "few valves" in description:
        params["valve_count"] = 2
    if "high cooling" in description:
        params["cooling_fins"] = True
    return params

def parse_crankcase(description):
    description = description.lower().strip()
    params = {
        "length": 500.0,
        "width": 300.0,
        "height": 200.0,
        "oil_pan_depth": 100.0,
        "flange_thickness": 15.0,
        "cylinder_count": 4
    }
    if "long" in description:
        params["length"] = 600.0
    elif "short" in description:
        params["length"] = 400.0
    if "wide" in description:
        params["width"] = 350.0
    elif "narrow" in description:
        params["width"] = 250.0
    if "deep oil pan" in description:
        params["oil_pan_depth"] = 120.0
    elif "shallow oil pan" in description:
        params["oil_pan_depth"] = 80.0
    if "many cylinders" in description:
        params["cylinder_count"] = 6
    elif "few cylinders" in description:
        params["cylinder_count"] = 2
    return params

def parse_engine_valve(description):
    description = description.lower().strip()
    params = {
        "valve_type": "intake",
        "stem_length": 100.0,
        "stem_diameter": 6.0,
        "head_diameter": 30.0,
        "head_thickness": 4.0,
        "filleted": False
    }
    if "exhaust" in description:
        params["valve_type"] = "exhaust"
        params["head_diameter"] = 25.0
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
    if params["head_diameter"] < params["stem_diameter"] * 3:
        params["head_diameter"] = params["stem_diameter"] * 3
    if params["head_thickness"] > params["head_diameter"] / 4:
        params["head_thickness"] = params["head_diameter"] / 4
    return params

# Component generation functions
def generate_camshaft(params):
    shaft = trimesh.creation.cylinder(radius=params["diameter"]/2, height=params["length"], segments=50)
    camshaft = shaft
    lobe_spacing = params["length"] / (params["lobe_count"] + 1)
    for i in range(params["lobe_count"]):
        lobe = trimesh.creation.cylinder(radius=params["diameter"]/2 + params["lobe_height"], height=10.0, segments=50)
        lobe.apply_translation([0, 0, (i + 1) * lobe_spacing - params["length"]/2])
        camshaft = camshaft.union(lobe)
    return camshaft

def generate_connecting_rod(params):
    big_end = trimesh.creation.cylinder(radius=params["big_end_diameter"]/2, height=params["thickness"], segments=50)
    small_end = trimesh.creation.cylinder(radius=params["small_end_diameter"]/2, height=params["thickness"], segments=50)
    small_end.apply_translation([0, params["length"], 0])
    body = trimesh.creation.box(extents=[params["thickness"], params["length"], params["thickness"]])
    body.apply_translation([0, params["length"]/2, 0])
    return trimesh.util.concatenate([big_end, small_end, body])

def generate_crankshaft(params):
    main_journal = trimesh.creation.cylinder(radius=params["journal_diameter"]/2, height=params["length"], segments=50)
    crankshaft = main_journal
    throw_spacing = params["length"] / (params["throw_count"] + 1)
    for i in range(params["throw_count"]):
        throw = trimesh.creation.cylinder(radius=params["journal_diameter"]/2, height=20.0, segments=50)
        throw.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0]))
        throw.apply_translation([params["throw_length"], 0, (i + 1) * throw_spacing - params["length"]/2])
        crankshaft = crankshaft.union(throw)
    return crankshaft

def generate_cylinder_head(params):
    head = trimesh.creation.box(extents=[params["length"], params["width"], params["height"]])
    valve_spacing = params["length"] / (params["valve_count"] + 1)
    for i in range(params["valve_count"]):
        valve_hole = trimesh.creation.cylinder(radius=15.0, height=params["height"] + 0.1, segments=50)
        valve_hole.apply_translation([(i + 1) * valve_spacing - params["length"]/2, 0, 0])
        head = head.difference(valve_hole)
    if params["cooling_fins"]:
        for i in range(5):
            fin = trimesh.creation.box(extents=[params["length"] * 0.8, 10.0, params["height"] * 0.8])
            fin.apply_translation([0, (i - 2) * 20, 0])
            head = head.union(fin)
    head.apply_translation([0, 0, params["height"]/2])
    return head

def generate_crankcase(params):
    main_housing = trimesh.creation.box(extents=[params["length"], params["width"], params["height"]])
    main_housing.apply_translation([0, 0, params["height"]/2])
    bearing_spacing = params["length"] / (params["cylinder_count"] + 1)
    crankcase = main_housing
    for i in range(params["cylinder_count"]):
        bearing = trimesh.creation.cylinder(radius=25.0, height=params["width"], segments=50)
        bearing.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0]))
        bearing.apply_translation([(i + 1) * bearing_spacing - params["length"]/2, 0, params["height"]/2])
        crankcase = crankcase.difference(bearing)
    oil_pan = trimesh.creation.box(extents=[params["length"] * 0.8, params["width"] * 0.9, params["oil_pan_depth"]])
    oil_pan.apply_translation([0, 0, -params["oil_pan_depth"]/2])
    crankcase = crankcase.union(oil_pan)
    flange_x_positions = [-params["length"]/2, params["length"]/2]
    for x_pos in flange_x_positions:
        for y_offset in [-params["width"]/2, params["width"]/2]:
            flange = trimesh.creation.box(extents=[params["flange_thickness"], 50.0, params["height"]])
            flange.apply_translation([x_pos, y_offset, params["height"]/2])
            crankcase = crankcase.union(flange)
    return crankcase

def generate_engine_valve(params):
    stem = trimesh.creation.cylinder(radius=params["stem_diameter"]/2, height=params["stem_length"], segments=50)
    stem.apply_translation([0, 0, params["stem_length"]/2])
    head = trimesh.creation.cylinder(radius=params["head_diameter"]/2, height=params["head_thickness"], segments=50)
    head.apply_translation([0, 0, params["stem_length"]])
    groove = trimesh.creation.cylinder(radius=params["stem_diameter"]/2 - 0.5, height=2.0, segments=50)
    groove.apply_translation([0, 0, params["stem_length"] - 5.0])
    valve = stem.union(head).difference(groove)
    if params["filleted"]:
        fillet_radius = (params["head_diameter"]/2 + params["stem_diameter"]/2) / 2
        fillet = trimesh.creation.cone(radius=fillet_radius, height=5.0, segments=50)
        fillet.apply_translation([0, 0, params["stem_length"] - 2.5])
        valve = valve.union(fillet)
    return valve

# Main function
def main():
    print("Supported components:", ", ".join(COMPONENTS))
    print("Enter component type and description (e.g., 'Component: camshaft, Description: long with many lobes')")
    print("Type 'exit' to quit.")
    
    while True:
        user_input = input("\nEnter input: ").strip()
        if user_input.lower() == "exit":
            print("Exiting program.")
            break
        
        # Parse input
        try:
            component_match = re.search(r"Component:\s*(\w+)", user_input, re.IGNORECASE)
            description_match = re.search(r"Description:\s*(.+)", user_input, re.IGNORECASE)
            
            if not component_match:
                print("Error: Please specify a component type (e.g., 'Component: camshaft').")
                continue
            component = component_match.group(1).lower()
            if component not in [c.lower() for c in COMPONENTS]:
                print(f"Error: Invalid component '{component}'. Choose from: {', '.join(COMPONENTS)}")
                continue
            
            description = description_match.group(1).strip() if description_match else ""
            if not description:
                print("Warning: No description provided. Using default parameters.")
            
            # Map component to parsing and generation functions
            component_functions = {
                "camshaft": (parse_camshaft, generate_camshaft),
                "connecting_rod": (parse_connecting_rod, generate_connecting_rod),
                "crankshaft": (parse_crankshaft, generate_crankshaft),
                "cylinder_head": (parse_cylinder_head, generate_cylinder_head),
                "crankcase": (parse_crankcase, generate_crankcase),
                "engine_valve": (parse_engine_valve, generate_engine_valve)
            }
            
            parse_fn, generate_fn = component_functions[component]
            
            # Parse parameters
            params = parse_fn(description)
            print(f"Parameters: {params}")
            
            # Generate model
            model = generate_fn(params)
            
            # Export STL
            output_filename = f"user_{component}.stl"
            output_filepath = os.path.join(OUTPUT_DIR, output_filename)
            try:
                model.export(output_filepath)
                print(f"Successfully generated: {os.path.abspath(output_filepath)}")
            except Exception as e:
                print(f"Error exporting {output_filepath}: {e}")
                continue
            
        except Exception as e:
            print(f"Error processing input: {e}")
            print("Please use format: 'Component: <type>, Description: <description>'")
            continue

if __name__ == "__main__":
    main()