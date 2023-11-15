import os
import boto3
import sys

# Get the index of the array job and size of the array job from the environment variables set by AWS Batch
int_idx_array = int(os.environ['AWS_BATCH_JOB_ARRAY_INDEX'])
array_size = int(os.environ['AWS_BATCH_JOB_ARRAY_SIZE'])
job_id = os.environ['AWS_BATCH_JOB_ID'] # Get the job ID to use as a unique identifier ex: 4fce4f74-96e4-4188-a07f-36898cfd75ab:29/
job_id_without_index = job_id.split(':')[0]

print(f"Matrix Index: {int_idx_array}")
print(f"Array Size Job: {array_size}")
print(f"Job ID: {job_id}")
print(f"Job Id Without Index: {job_id_without_index}")

# File path to the Blender file
blender_file_path = '/batch_scene.blend'

# Output path for the rendered images
output_path = '/tmp/'

blender_executable = '/usr/bin/blender'
render_script = '/render.py'
camera_script = '/cameras_ngp.py'


# If the index of the array job is the last one, run cameras_ngp.py to generate the JSON file
if int_idx_array + 1 == array_size:
    print("Ejecutando cameras_ngp.py")

    # Set the output path for the JSON file
    json_output_path = os.path.join(output_path, f"transforms_train.json")

    camera_command = f"{blender_executable} -b -P {camera_script} -- {blender_file_path} {json_output_path}"
    print(camera_command)

    os.system(camera_command)

    # S3 bucket and key for the JSON file
    bucket_name = 'blender-batch-render'
    s3_key = f'test-batch/{job_id_without_index}/transforms_train.json'

    def copy_to_s3(file_path, bucket_name, s3_key):
        s3 = boto3.client('s3')
        try:
            s3.upload_file(file_path, bucket_name, s3_key)
            print(f"JSON file successfully uploaded to S3 in bucket {bucket_name} with key {s3_key}.")
        except Exception as e:
            print(f"Error uploading content to S3: {str(e)}")
            sys.exit(1)

    # Upload the JSON file to S3 after cameras_ngp.py has been executed. 
    copy_to_s3(json_output_path, bucket_name, s3_key)

else:
    # Logic to render the images
    frame_start = int_idx_array
    frame_end = int_idx_array
    render_frame = int_idx_array

    script_args = [
        blender_file_path,
        output_path,
        str(frame_start),
        str(frame_end),
        str(render_frame)
    ]

    print(script_args)

    render_command = f"{blender_executable} -b -P {render_script} -- {' '.join(script_args)}"
    print(render_command)

    os.system(render_command)

    # Upload the rendered image to S3
    bucket_name = 'blender-batch-render'
    s3_key = f'test-batch/{job_id_without_index}/train/{int_idx_array:04d}.png'

    def copy_to_s3(file_path, bucket_name, s3_key):
        s3 = boto3.client('s3')
        try:
            s3.upload_file(file_path, bucket_name, s3_key)
            print(f"Render successfully uploaded to S3 in bucket {bucket_name} with key {s3_key}.")
        except Exception as e:
            print(f"Error uploading content to S3: {str(e)}")
            sys.exit(1)

    # Upload the rendered image to S3 after it has been rendered
    rendered_file_path = os.path.join(output_path, f"{int_idx_array:04d}.png")
    copy_to_s3(rendered_file_path, bucket_name, s3_key)
