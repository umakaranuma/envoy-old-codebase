import boto3
import os
import mimetypes
from datetime import datetime, timedelta
import requests
from botocore.config import Config

# -------------------------------
# S3 upload service (optimized)
# -------------------------------

class S3UploadService:
    # Connection pool and timeout configuration
    _s3_client = None
    _session = None
    
    @staticmethod
    def _get_session():
        """Get or create a requests session with connection pooling."""
        if S3UploadService._session is None:
            S3UploadService._session = requests.Session()
            # Configure connection pooling
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=3
            )
            S3UploadService._session.mount('http://', adapter)
            S3UploadService._session.mount('https://', adapter)
        return S3UploadService._session
    
    @staticmethod
    def _client():
        """Get or create S3 client with optimized configuration."""
        if S3UploadService._s3_client is None:
            # Optimized S3 client configuration
            config = Config(
                region_name=os.getenv("S3_REGION"),
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                max_pool_connections=20,
                connect_timeout=10,
                read_timeout=30
            )
            
            S3UploadService._s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
                config=config
            )
        return S3UploadService._s3_client

    @staticmethod
    def upload_file(file_content: bytes, file_name: str):
        """
        Legacy: upload from in-memory bytes. Kept for compatibility.
        """
        file_type, _ = mimetypes.guess_type(file_name)
        if not file_type:
            file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        s3_client = S3UploadService._client()
        bucket_name = os.getenv("S3_BUCKET_NAME")
        s3_key = f"exports/risks/{file_name}"

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file_content,
            ContentType=file_type
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600
        )
        return {"file_url": presigned_url, "file_name": file_name}

    @staticmethod
    def upload_stream_from_url(file_url: str, file_name: str):
        """
        Stream a remote file (exporter download URL) directly to S3.
        Optimized with connection pooling and timeouts.
        """
        file_type, _ = mimetypes.guess_type(file_name)
        if not file_type:
            file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        s3_client = S3UploadService._client()
        bucket_name = os.getenv("S3_BUCKET_NAME")
        s3_key = f"exports/risks/{file_name}"

        # Use session with connection pooling
        session = S3UploadService._get_session()
        
        # Optimized request with timeouts
        with session.get(file_url, stream=True, timeout=(10, 60)) as resp:
            resp.raise_for_status()
            # Stream response.raw to S3
            s3_client.upload_fileobj(
                resp.raw,
                bucket_name,
                s3_key,
                ExtraArgs={"ContentType": file_type}
            )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600
        )
        return {"file_url": presigned_url, "file_name": file_name}