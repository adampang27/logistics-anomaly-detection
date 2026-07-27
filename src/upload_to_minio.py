import os
import boto3
from botocore.exceptions import ClientError
import datetime

def main():

    # Resolve absolute path to dummy_logistics_data.csv
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "dummy_logistics_data.csv")
    # Initialize S3 client for MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin'
    )

    # Ask MinIO if bucket exists
    try: 
        s3_client.head_bucket(Bucket="logistics-data")
    # If MinIO responds with a 404 error
    except ClientError:
        s3_client.create_bucket(Bucket="logistics-data")

    today = datetime.date.today()
    key = f"year={today.year}/month={today.month:02d}/day={today.day:02d}/batch.csv"

    # Uploads a local file
    s3_client.upload_file(Filename=csv_path,Bucket="logistics-data",Key=key)

    # Confirmation
    print(f"Uploaded to logistics-data/{key}")
    
if __name__ == "__main__":
    main()