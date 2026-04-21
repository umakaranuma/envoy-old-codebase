"""
S3 Presigned URL Service

This service provides secure file upload and download functionality using AWS S3 presigned URLs.
Instead of exposing AWS credentials in URLs, this service generates temporary, secure URLs
that expire after a specified time.

Key Features:
- Secure file uploads with presigned POST URLs
- Secure file downloads with presigned GET URLs
- Unique file naming using nanoid
- Configurable expiration times
- Support for streaming uploads from remote URLs

Usage Examples:
1. Generate presigned upload URL for direct client uploads:
   upload_data = S3PresignedService.get_presigned_upload_url("document.pdf", "application/pdf", "documents")
   
2. Upload file content directly:
   result = S3PresignedService.upload_file_to_s3(file_content, "report.xlsx", "reports")
   
3. Stream remote file to S3:
   result = S3PresignedService.upload_stream_from_url("https://example.com/file.xlsx", "downloaded.xlsx")
   
4. Generate download URL:
   download_url = S3PresignedService.generate_presigned_download_url("path/to/file.xlsx", expires_in=3600)
"""

import boto3
import os
from nanoid import generate  # pip install nanoid

class S3PresignedService:
    """S3 service for generating presigned URLs with secure access"""
    
    _s3_client = None
    
    @staticmethod
    def _get_client():
        """Get or create S3 client with optimized configuration."""
        if S3PresignedService._s3_client is None:
            from botocore.config import Config
            
            # Configure S3 client to use signature version 4
            config = Config(
                signature_version='s3v4',
                region_name=os.getenv("S3_REGION")
            )
            
            S3PresignedService._s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
                config=config
            )
        return S3PresignedService._s3_client

    @staticmethod
    def generate_presigned_post(file_name: str, file_type: str, folder: str):
        """Generate a presigned URL and form fields for direct S3 upload"""
        key = f"{folder}/{generate()}_{file_name}"

        s3_client = S3PresignedService._get_client()
        response = s3_client.generate_presigned_post(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=key,
            Fields={
                "Content-Type": file_type,
            },
            Conditions=[
                {"Content-Type": file_type},
            ],
            ExpiresIn=3600,  # 1 hour
        )

        return {
            "url": response["url"],
            "fields": response["fields"],
            "key": key,
        }

    @staticmethod
    def generate_presigned_download_url(file_key: str, expires_in: int = 3600):
        """Generate a presigned URL for downloading a file from S3 using AWS Signature Version 4"""
        s3_client = S3PresignedService._get_client()
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv("S3_BUCKET_NAME"),
                'Key': file_key
            },
            ExpiresIn=expires_in,
            HttpMethod='GET'
        )
        
        return presigned_url

    @staticmethod
    def upload_file_to_s3(file_content: bytes, file_name: str, folder: str = "exports/risks"):
        """Upload file to S3 and return presigned download URL"""
        import mimetypes
        
        file_type, _ = mimetypes.guess_type(file_name)
        if not file_type:
            file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # Generate unique key with nanoid
        key = f"{folder}/{generate()}_{file_name}"
        
        s3_client = S3PresignedService._get_client()
        
        # Upload file to S3
        s3_client.put_object(
            Bucket=os.getenv("S3_BUCKET_NAME"),
            Key=key,
            Body=file_content,
            ContentType=file_type
        )

        # Generate presigned download URL
        presigned_url = S3PresignedService.generate_presigned_download_url(key)
        
        return {
            "file_url": presigned_url,
            "file_name": file_name,
            "file_key": key
        }

    @staticmethod
    def upload_stream_from_url(file_url: str, file_name: str, folder: str = "exports/risks"):
        """Stream a remote file directly to S3 and return presigned download URL"""
        import mimetypes
        import requests
        
        file_type, _ = mimetypes.guess_type(file_name)
        if not file_type:
            file_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # Generate unique key with nanoid
        key = f"{folder}/{generate()}_{file_name}"
        
        s3_client = S3PresignedService._get_client()
        
        # Stream the remote file directly to S3
        with requests.get(file_url, stream=True, timeout=(10, 60)) as resp:
            resp.raise_for_status()
            s3_client.upload_fileobj(
                resp.raw,
                os.getenv("S3_BUCKET_NAME"),
                key,
                ExtraArgs={"ContentType": file_type}
            )

        # Generate presigned download URL
        presigned_url = S3PresignedService.generate_presigned_download_url(key)
        
        return {
            "file_url": presigned_url,
            "file_name": file_name,
            "file_key": key
        }

    @staticmethod
    def get_presigned_upload_url(file_name: str, file_type: str, folder: str = "uploads"):
        """
        Get presigned URL for direct client-side upload to S3.
        This is useful for frontend applications that want to upload files directly to S3.
        """
        return S3PresignedService.generate_presigned_post(file_name, file_type, folder)
