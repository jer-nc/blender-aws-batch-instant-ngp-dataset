import bpy
import sys
import os

# Get arguments from the command line (blender -b -P render.py -- <blender_file_path> <output_path> <frame_start> <frame_end> <render_frame>)
blender_file_path = sys.argv[-5]
output_path = sys.argv[-4]
frame_start = int(sys.argv[-3])
frame_end = int(sys.argv[-2])
render_frame = int(sys.argv[-1])

# Open the blender file and set the frame range
bpy.ops.wm.open_mainfile(filepath=blender_file_path)
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end
bpy.context.scene.frame_set(render_frame)

# Configure the render settings (output path, file format)
bpy.context.scene.render.filepath = os.path.join(output_path, f"{render_frame:04d}")
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render the image and save it to the output path
bpy.ops.render.render(write_still=True)

# Quit Blender after rendering
bpy.ops.wm.quit_blender()
