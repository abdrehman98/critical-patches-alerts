import os
import json
import boto3
import requests
from datetime import datetime

# Environment Variables
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK', 'https://test.com')
REGION = 'us-east-1'
PATCH_GROUP = 'Production'


def get_ec2_client(region):
    """
    It will return EC2 client
    """
    client = boto3.client('ec2', region_name=region)
    return client


def get_ssm_client(region):
    """
    It will return SSM client
    """
    client = boto3.client('ssm', region_name=region)
    return client


def get_ec2_instance_id(patch_group):
    """
    It will return instance_id of any instance from patch_group
    """
    client = get_ec2_client(REGION)
    metadata = client.describe_instances(
        Filters=[
        {
            'Name': 'tag:Patch Group',
            'Values': [
                patch_group,
            ]
        },
    ])
    instance_id = metadata['Reservations'][0]['Instances'][0]['InstanceId']
    return instance_id


def get_last_patching_date(patch_group):
    """
    It will return last date(datetime object) of patching of patch_group
    """
    instance_id = get_ec2_instance_id(patch_group)
    client = get_ssm_client(REGION)
    metadata = client.describe_instance_patch_states(
        InstanceIds=[
            instance_id,
        ],
    )
    last_patching_date = metadata['InstancePatchStates'][0]['OperationEndTime']
    return last_patching_date


def get_release_date_of_latest_critical_patch():
    """
    It will return release date(datetime object) of latest critical patch released
    """
    client = get_ssm_client(REGION)
    metadata = client.describe_available_patches(
        Filters=[
            {
                'Key': 'PRODUCT',
                'Values': [
                    'AmazonLinux2.0',
                ]
                
            },
            {
                'Key': 'SEVERITY',
                'Values': [
                    'Critical',
                ]
                
            },
        ],
    )
    critial_patch_data = metadata['Patches'][0]['ReleaseDate']
    return critial_patch_data


def generate_slack_notification(SLACK_WEBHOOK, notification):
    """
    It will generate Slack Notification
    """
    headers = {'Content-type': 'application/json'}
    requests.post(url=SLACK_WEBHOOK, data=json.dumps(notification), headers=headers)
    return


def is_there_new_critical_patch(patch_group):
    """
    It will return True if there is a new critical patch relased and we havent patched 
    our patch_group other wise it will return False
    """
    critial_patch_data = get_release_date_of_latest_critical_patch()
    last_patching_date = get_last_patching_date(patch_group)
    if(last_patching_date < critial_patch_data):
        notification = {          
            "icon_emoji": ":rotating_light:",
            "text": "*New Critical Patch Available*:\nPatch Released on " + critial_patch_data.strftime("%m/%d/%Y") + "\nWe installed patches last time on " + last_patching_date.strftime("%m/%d/%Y")
        }
        generate_slack_notification(SLACK_WEBHOOK, notification)
        return True

    return False

def lambda_handler(event, context):
    """
    Lambda handler
    """
    print(event)
    if(is_there_new_critical_patch(PATCH_GROUP)):
        print("Slack Notification Generated")
    else:
        print("No New Messages")