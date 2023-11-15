import bpy
import sys
import os
import json

# Get the path to the blender file from the command line arguments
blender_file_path = sys.argv[-2]


print("blender_file_path: ", blender_file_path)

bpy.ops.wm.open_mainfile(filepath=blender_file_path)

# function from original nerf 360_view.py code for blender
def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list

# Function to find the camera object in the scene
def find_camera(scene):
    for obj in scene.objects:
        if obj.type == 'CAMERA' and obj.name == 'BNGP_CAMERA':
            return obj 
    return None  

# Get the camera object from the scene
camera_object = find_camera(bpy.context.scene)

def find_aabb(scene):
    for obj in scene.objects:
        if obj.type == 'MESH' and obj.name == 'BNGP_AABB':
            return obj 
    return None

print("camera_object: ", camera_object)

aabb_object = find_aabb(bpy.context.scene)

# Verify aaBB object exists in the scene
if aabb_object is not None:
    # Get the scale of the aabb object
    scale_x, scale_y, scale_z = aabb_object.scale

    print(f"Scale of BNGP_AABB: X={scale_x}, Y={scale_y}, Z={scale_z}")
else:
    print("'BNGP_AABB' Not found")

if camera_object is not None:
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    camera_angle_x = camera_object.data.angle_x
    camera_angle_y = camera_object.data.angle_y

    # camera properties
    f_in_mm = camera_object.data.lens # focal length in mm
    scale = bpy.context.scene.render.resolution_percentage / 100
    width_res_in_px = bpy.context.scene.render.resolution_x * scale # width
    height_res_in_px = bpy.context.scene.render.resolution_y * scale # height
    optical_center_x = width_res_in_px / 2
    optical_center_y = height_res_in_px / 2

    # pixel aspect ratios
    size_x = bpy.context.scene.render.pixel_aspect_x * width_res_in_px
    size_y = bpy.context.scene.render.pixel_aspect_y * height_res_in_px
    pixel_aspect_ratio = bpy.context.scene.render.pixel_aspect_x / bpy.context.scene.render.pixel_aspect_y

    # sensor fit and sensor size (and camera angle swap in specific cases)
    if camera_object.data.sensor_fit == 'AUTO':
        sensor_size_in_mm = camera_object.data.sensor_height if width_res_in_px < height_res_in_px else camera_object.data.sensor_width
        if width_res_in_px < height_res_in_px:
            sensor_fit = 'VERTICAL'
            camera_angle_x, camera_angle_y = camera_angle_y, camera_angle_x
        elif width_res_in_px > height_res_in_px:
            sensor_fit = 'HORIZONTAL'
        else:
            sensor_fit = 'VERTICAL' if size_x <= size_y else 'HORIZONTAL'

    else:
        sensor_fit = camera_object.data.sensor_fit
        if sensor_fit == 'VERTICAL':
            sensor_size_in_mm = camera_object.data.sensor_height if width_res_in_px <= height_res_in_px else camera_object.data.sensor_width
            if width_res_in_px <= height_res_in_px:
                camera_angle_x, camera_angle_y = camera_angle_y, camera_angle_x

    # focal length for horizontal sensor fit
    if sensor_fit == 'HORIZONTAL':
        sensor_size_in_mm = camera_object.data.sensor_width
        s_u = f_in_mm / sensor_size_in_mm * width_res_in_px
        s_v = f_in_mm / sensor_size_in_mm * width_res_in_px * pixel_aspect_ratio

    # focal length for vertical sensor fit
    if sensor_fit == 'VERTICAL':
        s_u = f_in_mm / sensor_size_in_mm * width_res_in_px / pixel_aspect_ratio
        s_v = f_in_mm / sensor_size_in_mm * width_res_in_px

    # Create the transforms_train.json file
    camera_data = {
        "camera_angle_x": camera_angle_x,
        "camera_angle_y": camera_angle_y,
        "fl_x": s_u,
        "fl_y": s_v,
        'k1': 0.0,
        'k2': 0.0,
        'p1': 0.0,
        'p2': 0.0,
        "cx": optical_center_x,
        "cy": optical_center_y,
        "w": width_res_in_px,
        "h": height_res_in_px,
        "aabb_scale": int(aabb_object.scale.x),
        "frames": []
    }

    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)

        camera_data["frames"].append({
            "file_path": f"train\\{frame:04d}.png",
            "transform_matrix": listify_matrix(camera_object.matrix_world)
        })

    # Save the JSON file to /tmp 
    json_output_path = os.path.join("/tmp", "transforms_train.json")
    with open(json_output_path, "w") as json_file:
        json.dump(camera_data, json_file)

    print(f"JSON saved Succesfully {json_output_path}")
else:
    print("'BNGP_CAMERA' Not found")