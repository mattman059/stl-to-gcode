import numpy as np
from stl import mesh
import math

def load_stl(file_path):
    """Load an STL file and return its mesh."""
    return mesh.Mesh.from_file(file_path)

def calculate_plane_intersection(triangle, z):
    """Calculate the intersection of a triangle with a horizontal plane at height z."""
    vertices = triangle.reshape(3, 3)
    intersections = []

    for i in range(3):
        p1, p2 = vertices[i], vertices[(i + 1) % 3]
        z1, z2 = p1[2], p2[2]

        if z1 == z and z2 == z:
            # Edge lies on the plane
            intersections.extend([p1[:2], p2[:2]])
        elif (z1 < z <= z2) or (z2 < z <= z1):
            # Compute intersection
            t = (z - z1) / (z2 - z1)
            intersect_point = p1 + t * (p2 - p1)
            intersections.append(intersect_point[:2])

    return intersections

def slice_model(mesh_data, layer_height):
    """Slice the model into layers at the given height intervals."""
    z_min, z_max = mesh_data.z.min(), mesh_data.z.max()
    layers = []
    z = z_min

    while z <= z_max:
        layer_edges = []
        for triangle in mesh_data.vectors:
            intersections = calculate_plane_intersection(triangle, z)
            if len(intersections) == 2:
                layer_edges.append(intersections)

        layers.append(layer_edges)
        z += layer_height

    return layers

def generate_toolpaths(layers):
    """Generate toolpaths for each layer."""
    toolpaths = []

    for layer in layers:
        path = []
        for edge in layer:
            path.extend(edge)

        # Simple sorting for visualization; replace with proper path optimization
        if path:
            path = sorted(path, key=lambda p: (p[0], p[1]))

        toolpaths.append(path)

    return toolpaths

def generate_gcode(toolpaths, layer_height, output_file):
    """Convert toolpaths to GCODE and write to a file."""
    with open(output_file, 'w') as gcode_file:
        gcode_file.write("G21 ; Set units to mm\n")
        gcode_file.write("G90 ; Absolute positioning\n")
        gcode_file.write("M104 S200 ; Set extruder temperature\n")
        gcode_file.write("M140 S60 ; Set bed temperature\n")
        gcode_file.write("M190 S60 ; Wait for bed temperature\n")
        gcode_file.write("M109 S200 ; Wait for extruder temperature\n")

        z = 0
        for layer in toolpaths:
            z += layer_height
            gcode_file.write(f"G1 Z{z:.2f} F300 ; Move to layer height\n")

            for x, y in layer:
                gcode_file.write(f"G1 X{x:.2f} Y{y:.2f} F1500 ; Move\n")

        gcode_file.write("M104 S0 ; Turn off extruder\n")
        gcode_file.write("M140 S0 ; Turn off bed\n")
        gcode_file.write("M84 ; Disable motors\n")

# Example usage
if __name__ == "__main__":
    stl_file = "INPUT_FILENAME_HERE"
    gcode_file = "OUTPUT_FILENAME_HERE"
    layer_height = 0.2

    # Load the STL file
    mesh_data = load_stl(stl_file)

    # Slice the model
    layers = slice_model(mesh_data, layer_height)

    # Generate toolpaths
    toolpaths = generate_toolpaths(layers)

    # Generate GCODE
    generate_gcode(toolpaths, layer_height, gcode_file)

    print(f"GCODE file saved to {gcode_file}")
