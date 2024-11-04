import bpy
import os
import math
from mathutils import Vector, Euler
import numpy as np

def create_slices_from_orientation(obj, num_slices):
    # Calculate the normal vector from the object's Euler angles
    euler_angles = obj.rotation_euler
    normal_vector = euler_angles.to_matrix() @ Vector((0, 0, 1))
    normal_vector.normalize()

    # Ensure the object is selected and active
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    # Get the bounding box corners in world space
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # Find the minimum and maximum coordinates along the normal vector
    min_coord = min(bbox, key=lambda v: v.dot(normal_vector))
    max_coord = max(bbox, key=lambda v: v.dot(normal_vector))

    min_dot = min_coord.dot(normal_vector)
    max_dot = max_coord.dot(normal_vector)

    slice_spacing = (max_dot - min_dot) / num_slices

    sliced_objects = []

    for i in range(num_slices + 1):
        dot_loc = min_dot + i * slice_spacing
        point_on_plane = min_coord + normal_vector * (i * slice_spacing)

        # Create a plane at the slice position
        bpy.ops.mesh.primitive_plane_add(size=5, location=point_on_plane)
        plane = bpy.context.object
        plane.rotation_euler = normal_vector.to_track_quat('Z', 'Y').to_euler()

        obj_copy = obj.copy()
        obj_copy.data = obj.data.copy()
        bpy.context.collection.objects.link(obj_copy)
        sliced_objects.append(obj_copy)
        mod = obj_copy.modifiers.new(name=f'Slice_{i}', type='BOOLEAN')
        mod.operation = 'INTERSECT'
        mod.object = plane
        bpy.context.view_layer.objects.active = obj_copy
        bpy.ops.object.modifier_apply(modifier=mod.name)

        bpy.data.objects.remove(plane, do_unlink=True)

    return sliced_objects
def create_infill():
    
def extract_vertices_and_normals(obj):
    vertices_and_normals = []
    for vertex in obj.data.vertices:
        world_vertex = obj.matrix_world @ vertex.co
        world_normal = obj.matrix_world.to_3x3() @ vertex.normal
        vertices_and_normals.append((world_vertex.x, world_vertex.y, world_vertex.z, world_normal.x, world_normal.y, world_normal.z))
    return vertices_and_normals

def generate_gcode(vertices_and_normals):
    gcode = []
    for v in vertices_and_normals:
        x, y, z, i, j, k = v
        gcode.append(f"G01 X{x:.3f} Y{y:.3f} Z{z:.3f} I{i:.3f} J{j:.3f} K{k:.3f}")
    return gcode

def printer(data):
    result = f"{data[0]} X{data[1]:.4f} Y{data[2]:.4f} Z{data[3]:.4f} U{data[4]:.4f} V{data[5]:.4f}"
    return result

def rotmat(vec, ang):
    r = np.eye(3)
    k = np.array([[0, -vec[2], vec[1]], [vec[2], 0, -vec[0]], [-vec[1], vec[0], 0]])
    r += np.sin(ang) * k + (1 - np.cos(ang)) * np.dot(k, k)
    return r

def five(g):
    if len(g) != 7 or g[0] not in ['G00', 'G01']:
        raise ValueError("Invalid G-code command")
    norm = math.sqrt(g[4]**2 + g[5]**2 + g[6]**2)
    if norm == 0:
        return printer(('G01', 0, 0, 0, 0, 0))
    unit_vec = [g[4] / norm, g[5] / norm, g[6] / norm]

    u = np.arccos(unit_vec[2])
    v = np.arctan2(unit_vec[1], unit_vec[0])

    r = np.array([g[1], g[2], g[3]]).reshape((3, 1))
    R = rotmat([0, 1, 0], u) @ rotmat([0, 0, 1], v)
    r1 = R @ r
    return printer(('G01', r1[0][0], r1[1][0], r1[2][0], u, v))

def breaker(s):
    parts = s.split()
    result = (parts[0],)
    for part in parts[1:]:
        result += (float(part[1:]),)
    return result

def main():
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    obj = bpy.context.active_object
    if not obj:
        print("No active object selected")
        return

    num_slices = 10
    sliced_objects = create_slices_from_orientation(obj, num_slices)

    all_gcode = []
    for i, sliced_obj in enumerate(sliced_objects):
        vertices_and_normals = extract_vertices_and_normals(sliced_obj)
        gcode = generate_gcode(vertices_and_normals)
        all_gcode.extend(gcode)

        print(f"G-code for Sliced Object {i+1}:\n")
        print("\n".join(gcode))
        print("\n")

    five_axis = []
    for gcode_line in all_gcode:
        five_axis.append(five(breaker(gcode_line)))

    # Specify a writable directory (e.g., Documents folder)
    write_directory = os.path.expanduser("~/Documents")
    output_file_path = os.path.join(write_directory, "output_gcode.txt")

    # Save the G-code to a file
    with open(output_file_path, "w") as f:
        f.write("\n".join(all_gcode))

    print(f"G-code file saved at: {output_file_path}")

if __name__ == "__main__":
    main()
