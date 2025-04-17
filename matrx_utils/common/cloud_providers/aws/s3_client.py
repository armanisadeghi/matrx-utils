# common/cloud_providers/aws/s3_client.py

from matrx_utils.common.cloud_providers.aws.client import get_boto3_service_client
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from matrx_utils.common import vcprint

S3_INSTANCE = None


def get_s3_client():
    """
    Return a global S3 client instance.
    If not initialized, create a new instance.
    """
    global S3_INSTANCE

    if S3_INSTANCE is None:
        vcprint("Creating === NEW === S3 client (You should never see this twice)", color="light_yellow")
        S3_INSTANCE = get_boto3_service_client("s3")

    return S3_INSTANCE


def list_s3_buckets():
    """
    Example function to list all S3 buckets using the global S3 client instance.
    """
    s3 = get_s3_client()
    try:
        response = s3.list_buckets()
        return response.get('Buckets', [])
    except NoCredentialsError:
        raise Exception("AWS credentials are not available.")
    except PartialCredentialsError:
        raise Exception("AWS credentials are incomplete.")
    except Exception as e:
        raise Exception(f"Failed to list S3 buckets: {str(e)}")


if __name__ == "__main__":
    s3_client = get_s3_client()
    print("S3 Client:", s3_client)

    # Example usage
    try:
        buckets = list_s3_buckets()
        vcprint(buckets, pretty=True)
    except Exception as e:
        print("Error:", e)
