import bpy
import os
from mathutils import Vector

def create_slices_from_orientation(obj, num_slices, normal_vector):

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    min_coord = min(bbox, key=lambda v: v.dot(normal_vector))
    max_coord = max(bbox, key=lambda v: v.dot(normal_vector))
    
    min_dot = min_coord.dot(normal_vector)
    max_dot = max_coord.dot(normal_vector)
    
    slice_spacing = (max_dot - min_dot) / num_slices
    
    sliced_objects = []
    
 
    for i in range(1, num_slices):
        dot_loc = min_dot + i * slice_spacing


        point_on_plane = normal_vector * dot_loc
        point_on_plane_global = Vector((0, 0, 0)) 

        bpy.ops.mesh.primitive_plane_add(size=2, location=point_on_plane)
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

def main():
   
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    
    obj = bpy.context.active_object
    if not obj:
        print("No active object selected")
        return

   
    num_slices = 10

    normal_vector = Vector((0, 0, 1))  # Along the Z-axis as an example
    sliced_objects = create_slices_from_orientation(obj, num_slices, normal_vector)

    
    all_gcode = []
    for i, sliced_obj in enumerate(sliced_objects):
        vertices_and_normals = extract_vertices_and_normals(sliced_obj)
        gcode = generate_gcode(vertices_and_normals)
        all_gcode.extend(gcode)

       
        print(f"G-code for Sliced Object {i+1}:\n")
        print("\n".join(gcode))
        print("\n")

    write_directory = bpy.path.abspath("//")  
