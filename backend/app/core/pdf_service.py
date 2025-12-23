import os
import io
import uuid
import boto3
from jinja2 import Template
from weasyprint import HTML
from botocore.client import Config
from app.core.config import settings

# MinIO Config
MINIO_URL = os.getenv("MINIO_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET_NAME = "submissions"

# Initialize S3 Client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1" # MinIO default
)

# Ensure bucket exists
try:
    s3_client.head_bucket(Bucket=BUCKET_NAME)
except:
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        # Set public policy for testing or use presigned URLs?
        # For simplicity, we'll use presigned URLs.
    except Exception as e:
        print(f"Failed to create bucket: {e}")

class PDFService:
    @staticmethod
    def render_html(template_str: str, data: dict) -> str:
        """
        Renders HTML from a Jinja2 template string.
        """
        template = Template(template_str)
        return template.render(data)

    @staticmethod
    def generate_pdf_bytes(html_content: str) -> bytes:
        """
        Converts HTML string to PDF bytes using WeasyPrint.
        """
        return HTML(string=html_content).write_pdf()

    @staticmethod
    def upload_pdf(pdf_bytes: bytes) -> str:
        """
        Uploads PDF bytes to MinIO and returns a 7-day presigned URL.
        """
        filename = f"{uuid.uuid4()}.pdf"
        file_obj = io.BytesIO(pdf_bytes)
        
        s3_client.upload_fileobj(
            file_obj,
            BUCKET_NAME,
            filename,
            ExtraArgs={'ContentType': 'application/pdf'}
        )
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=604800  # 7 days
        )
        # Use localhost for URL if internal
        # The URL generated inside Docker says "minio:9000". 
        # For local dev access, we might need to swap host if running outside docker.
        # But if frontend uses it, it needs to reach minio.
        # For now, return as is.
        return url
        
pdf_service = PDFService()
