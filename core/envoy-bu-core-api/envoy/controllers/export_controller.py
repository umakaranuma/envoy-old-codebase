from datetime import datetime
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from openpyxl import Workbook
import os
import logging

from mServices.ResponseService import ResponseService

logger = logging.getLogger(__name__)

try:
    from botocore.exceptions import ClientError
    from envoy.services.s3_presigned_service import S3PresignedService
    BOTO3_AVAILABLE = True
except ImportError as e:
    logger.error(f"boto3 or botocore not available: {str(e)}")
    BOTO3_AVAILABLE = False
    ClientError = Exception  # Fallback for type hinting

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_receipts_excel(request):
    try:
        if not BOTO3_AVAILABLE:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": "Library not available"},
                "boto3 library is not installed. Please install it using: pip install boto3"
            )

        # Deterministic file name (change logic if needed)
        today = datetime.now().strftime("%Y%m%d")
        file_name = f"receipts_export_{today}.xlsx"
        folder = "exports/receipts"
        file_key = f"{folder}/{file_name}"

        s3_client = S3PresignedService._get_client()
        bucket = os.getenv("S3_BUCKET_NAME")

        if not bucket:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": "Configuration error"},
                "S3_BUCKET_NAME environment variable is not set"
            )

        # Build S3 URL only (no CDN) for s3_url in response
        region = os.getenv("S3_REGION")
        s3_url = None
        if region:
            s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{file_key}"
        # Build S3 URL only (no CDN) for s3_url in response
        region = os.getenv("S3_REGION")
        s3_url = None
        if region:
            s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{file_key}"

        # Check if file already exists in S3
        try:
            s3_client.head_object(Bucket=bucket, Key=file_key)

            # File exists → just return download URL
            download_url = S3PresignedService.generate_presigned_download_url(file_key)

            return ResponseService.response(
                "SUCCESS",
                {
                    "source": "s3_cached",
                    "file_url": download_url,
                    "file_name": file_name,
                    "s3_url": file_key,
                },
                "Excel file retrieved successfully"
            )

        except ClientError as e:
            # Check if it's a 404 (file not found) or other error
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code != '404':
                # It's a different error, log it
                logger.error(f"S3 head_object error: {str(e)}")
                # Continue to generate new file
            # File does not exist → generate new one
            pass

        # Generate Excel File
        wb = Workbook()
        ws = wb.active
        ws.title = "Receipts Export"

        headers = [
            "Receipt number",
            "Paid amount",
            "Insurer policy number",
            "Insurer invoice id"
        ]
        ws.append(headers)

        # TODO: Fetch and append real receipt data
        # Example:
        # receipts = Receipt.objects.all()
        # for r in receipts:
        #     ws.append([
        #         r.receipt_number,
        #         r.paid_amount,
        #         r.insurer_policy_number,
        #         r.insurer_invoice_id
        #     ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Upload to S3 (without nanoid, fixed key)
        s3_client.put_object(
            Bucket=bucket,
            Key=file_key,
            Body=output.getvalue(),
            ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Generate presigned download URL
        download_url = S3PresignedService.generate_presigned_download_url(file_key)

        return ResponseService.response(
            "SUCCESS",
            {
                "source": "generated",
                "file_url": download_url,
                "file_name": file_name,
                "s3_url":  file_key,
            },
            "Excel file generated and uploaded successfully"
        )

    except Exception as e:
        logger.error(f"Error exporting receipts to Excel: {str(e)}", exc_info=True)
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to export Excel file"
        )