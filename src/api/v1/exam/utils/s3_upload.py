import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from Config.config import settings
import os

def upload_file_to_s3(file, bucket_name: str, object_name: str):
    """
    Upload a file to an S3 bucket.
    
    Parameters:
        - file: The file object to upload
        - bucket_name: The S3 bucket name where the file will be stored
        - object_name: The desired object name in the S3 bucket (file name in S3)
        
    Returns:
        - True if the upload was successful, False otherwise
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        print(f"File uploaded successfully to {bucket_name}/{object_name}")
        return True
    except NoCredentialsError:
        print("Error: AWS credentials are not available.")
        return False
    except ClientError as e:
        print(f"Error uploading file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return False
