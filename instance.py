#!/usr/bin/env python3

import cgi
import cgitb
import json
import boto3
from botocore.exceptions import ClientError

# Enable CGI traceback for debugging
cgitb.enable()

# Print necessary headers
print("Content-Type: application/json\n")

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get the command field
command = form.getvalue('command')

def parse_command(command):
    """
    Parse the command string into parameters.

    Example command:
    "launch --type=t2.micro --image=ami-12345678 --region=us-east-1 --name=MyInstance"

    Returns:
    - A dictionary with parsed parameters.
    """
    params = {}
    if command:
        parts = command.split()
        for part in parts:
            if part.startswith("--"):
                key_value = part[2:].split("=")
                if len(key_value) == 2:
                    params[key_value[0]] = key_value[1]
    return params

def launch_aws_instance(instance_type, image_id, region_name, instance_name=None):
    """
    Launch an AWS EC2 instance with the specified parameters.

    Parameters:
    - instance_type: Type of EC2 instance (e.g., 't2.micro').
    - image_id: AMI ID for the instance.
    - region_name: AWS region (e.g., 'us-east-1').
    - instance_name: Name of the instance (optional).

    Returns:
    - A dictionary with success status and instance ID or error message.
    """
    try:
        # Use default credentials from environment or credentials file
        ec2 = boto3.client('ec2', region_name=region_name)

        # Launch the instance
        response = ec2.run_instances(
            InstanceType=instance_type,
            ImageId=image_id,
            MinCount=1,
            MaxCount=1
        )
        instance_id = response['Instances'][0]['InstanceId']

        # Optionally tag the instance with a name
        if instance_name:
            ec2.create_tags(
                Resources=[instance_id],
                Tags=[{"Key": "Name", "Value": instance_name}]
            )

        return {"success": True, "instance_id": instance_id}
    except ClientError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

# Parse the command into parameters
parameters = parse_command(command)

# Extract required parameters
instance_type = parameters.get('type')
image_id = parameters.get('image')
region_name = parameters.get('region')
instance_name = parameters.get('name')

# Validate input and launch the instance
if instance_type and image_id and region_name:
    result = launch_aws_instance(instance_type, image_id, region_name, instance_name)
else:
    result = {"success": False, "error": "Missing one or more required parameters in command"}

# Return the JSON result
print(json.dumps(result))
