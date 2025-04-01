# common/cloud_providers/aws/client.py

import os
import boto3
from dotenv import load_dotenv

aws_access_key_id = None
aws_secret_access_key = None
aws_region = None
boto3_service_instance = None


def init_aws_connection_details():
    """
    Initialize AWS connection details from environment variables.
    """
    global aws_access_key_id, aws_secret_access_key, aws_region, boto3_service_instance

    if aws_access_key_id is None:  # Load once
        load_dotenv()

        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region = os.environ.get("AWS_REGION")

        if not aws_access_key_id or not aws_secret_access_key or not aws_region:
            raise EnvironmentError(
                "AWS credentials or region not found in environment variables."
            )

        # Initialize the global boto3 service instance
        boto3_service_instance = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

def get_boto3_service_client(service_name):
    """
    Return a boto3 client for a specific AWS service using the global boto3 session.
    """
    if boto3_service_instance is None:
        init_aws_connection_details()

    return boto3_service_instance.client(service_name)



