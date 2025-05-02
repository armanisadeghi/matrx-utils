# common/aws/aws_client.py

import os
import boto3
import aioboto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from matrx_utils import vcprint

aws_access_key_id = None
aws_secret_access_key = None
aws_region = None
boto3_service_instance = None
s3_instance = None
_async_session = None

def init_aws_connection_details():
    global aws_access_key_id, aws_secret_access_key, aws_region, boto3_service_instance, _async_session

    if aws_access_key_id is None:
        load_dotenv()

        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_region = os.environ.get("AWS_REGION")

        if not aws_access_key_id or not aws_secret_access_key or not aws_region:
            raise EnvironmentError("AWS credentials or region not found in environment variables.")

        boto3_service_instance = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
        )

        _async_session = aioboto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        vcprint("[AWS S3] Singleton async session created", color="green")


def get_boto3_service_client(process_name):
    if boto3_service_instance is None:
        init_aws_connection_details()
    return boto3_service_instance.client(process_name)

def get_s3_client():
    global s3_instance
    if s3_instance is None:
        vcprint("[AWS S3] Singleton client created (sync)", color="green")
        s3_instance = get_boto3_service_client("s3")
    return s3_instance

async def get_async_s3_client_context_manager():
    global _async_session

    if _async_session is None:
        init_aws_connection_details()

    if _async_session is None:
         raise RuntimeError("Async AWS Session could not be initialized.")

    return _async_session.client("s3")
