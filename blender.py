import os
import bpy
import csv
import math
import random
import logging

logging.basicConfig(level=logging.INFO)

# Set the path to your CSV file
csv_file_path = ""  # The absolute path to the CSV with the network data.


# Function to create a small sphere at the given location with a white emissive material
def create_point(name, location):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=0.03, location=location
    )
    point = bpy.context.object
    point.name = name

    # Create white emissive material for the point
    material = bpy.data.materials.new(name="EmissiveWhite")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()

    emission_node = nodes.new("ShaderNodeEmission")
    emission_node.inputs["Strength"].default_value = 10
    emission_node.location = (-300, 300)

    output_node = nodes.new("ShaderNodeOutputMaterial")
    output_node.location = (0, 300)

    material.node_tree.links.new(
        emission_node.outputs["Emission"], output_node.inputs["Surface"]
    )

    point.data.materials.append(material)

    return point


# Create a single white principled bsdf shader for all edges
def create_edge_material():
    material = bpy.data.materials.new(name="EdgeShader")
    material.use_nodes = True

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Gradient Texture node
    gradient_node = nodes.new("ShaderNodeTexGradient")
    gradient_node.location = (-300, 300)
    gradient_node.gradient_type = "LINEAR"

    # Create ColorRamp node
    color_ramp_node = nodes.new("ShaderNodeValToRGB")
    color_ramp_node.location = (-100, 300)
    color_ramp_node.color_ramp.elements[0].color = (0, 0.725, 0.506, 1)  # Hex: #00B981
    color_ramp_node.color_ramp.elements.new(0.5)
    color_ramp_node.color_ramp.elements[1].color = (0.455, 0.737, 0, 1)  # Hex: #74BC00
    color_ramp_node.color_ramp.elements[2].color = (1, 1, 0, 1)  # Hex: #FFFF00

    # Create Principled BSDF node
    principled_bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf_node.location = (100, 300)

    # Create Output node
    output_node = nodes.new("ShaderNodeOutputMaterial")
    output_node.location = (300, 300)

    # Connect nodes
    links.new(gradient_node.outputs["Color"], color_ramp_node.inputs["Fac"])
    links.new(
        color_ramp_node.outputs["Color"], principled_bsdf_node.inputs["Base Color"]
    )
    links.new(principled_bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

    return material


edge_material = create_edge_material()


# Function to create a curved edge between two points (vertices) and apply the shared edge material
def create_curved_edge(point1, point2):
    p1, p2 = point1.location, point2.location
    midpoint = (p1 + p2) / 2
    control_point_distance = 2.0  # Increase this value to add more curvature
    control_point = (
        midpoint + ((p1 - p2).cross((0, 0, 1))).normalized() * control_point_distance
    )

    # Create the curve
    curve_data = bpy.data.curves.new("curved_edge", "CURVE")
    curve_data.dimensions = "3D"
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(2)  # Add two control points
    spline.bezier_points[0].co = p1
    spline.bezier_points[1].co = control_point
    spline.bezier_points[2].co = p2
    spline.bezier_points[
        0
    ].handle_right_type = "AUTO"  # Set handle type to AUTO for smoothness
    spline.bezier_points[
        2
    ].handle_left_type = "AUTO"  # Set handle type to AUTO for smoothness

    # Add thickness to the curve
    curve_data.bevel_depth = 0.03
    curve_data.resolution_u = 40  # Increase this value for smoother curves

    # Create curve object
    curve_obj = bpy.data.objects.new("curved_edge", curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Assign the shared edge material to the curve object
    curve_obj.data.materials.append(edge_material)

    return curve_obj


# Function to generate random non-conflicting coordinates within a maximum distance from the center
def generate_coordinates(existing_coords, max_distance=300.0, min_distance=1.0):
    while True:
        x = random.uniform(-max_distance, max_distance)
        y = random.uniform(-max_distance, max_distance)
        z = random.uniform(-max_distance, max_distance)

        if 2 * x**2 + 2 * y**2 + z**2 <= max_distance**2:
            new_coord = (x, y, z)
            return new_coord


# Read the CSV file and create the graph
points = {}
edges = []
existing_coords = []

# Create a collection for points and edges
graph_collection = bpy.data.collections.new("Graph")
bpy.context.scene.collection.children.link(graph_collection)

with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=",")
    next(csvreader)  # Skip header row

    for index, row in enumerate(csvreader):
        if (index + 1) % 100 == 0:
            logging.info(f"\t{100* ((index + 1)/18061)}%")
        source = row[1]
        target = row[2]
        if source not in points:
            coord = generate_coordinates(existing_coords)
            existing_coords.append(coord)
            points[source] = create_point(source, coord)
            bpy.context.scene.collection.objects.unlink(points[source])
            graph_collection.objects.link(points[source])  # Add point to the collection
        if target not in points:
            coord = generate_coordinates(existing_coords)
            existing_coords.append(coord)
            points[target] = create_point(target, coord)
            bpy.context.scene.collection.objects.unlink(points[target])
            graph_collection.objects.link(points[target])  # Add point to the collection

        edge = create_curved_edge(points[source], points[target])
        edges.append(edge)
        bpy.context.scene.collection.objects.unlink(edge)
        graph_collection.objects.link(edge)  # Add edge to the collection
