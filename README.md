# Blender 5-Axis G-Code Generator Script

This script automates slicing a 3D object in Blender along a specified orientation, extracting vertex and normal data from the slices, and generating G-code compatible with a 5-axis CNC machine or 3D printer. The G-code includes transformations and rotational commands for 5-axis machining.

## Overview
- **Slicing**: Slices the active Blender object into multiple layers based on its orientation.
- **Data Extraction**: Extracts world coordinates of vertices and normals from each slice.
- **G-code Generation**: Generates standard G-code commands for linear movements (`G1`) with position and orientation data.
- **5-Axis Transformation**: Adds necessary rotations (`B` and `C` axes) for 5-axis machining.
- **Output**: Final G-code is saved to a text file, ready for 5-axis machine use.

## Table of Contents
- Prerequisites
- Functions
  - `create_slices_from_orientation`
  - `extract_vertices_and_normals`
  - `generate_gcode`
  - `five_axis_transform`
  - `printer`
  - `breaker`
  - `main`
- Usage Instructions
- Notes
- Example Output
- Dependencies

## Prerequisites
- **Blender**: Run the script within Blender’s scripting environment.
- **Active Object**: Ensure an object is selected and active in Blender.
- **NumPy**: Required for mathematical computations.

## Functions

### `create_slices_from_orientation`
Slices a Blender object into layers along a specified orientation.
- **Parameters**: `obj` (Blender object), `num_slices` (int)
- **Returns**: `sliced_objects` (list)
- **Details**:
  - Computes normal vector and bounding box.
  - Determines slicing planes and aligns with slicing direction.
  - Adds each slice to the `sliced_objects` list.

```python
def create_slices_from_orientation(obj, num_slices):
    # [Function implementation]
