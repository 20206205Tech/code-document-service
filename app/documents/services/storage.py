import tempfile
from pathlib import Path
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError
from loguru import logger

import env
from utils.file_validation import get_content_type


class R2StorageError(Exception):
    pass


class R2StorageService:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=env.R2_ENDPOINT_URL,
            aws_access_key_id=env.R2_ACCESS_KEY_ID,
            aws_secret_access_key=env.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )
        self.bucket_name = env.R2_BUCKET_NAME
        logger.info(f"✅ R2 Storage Service initialized - Bucket: {self.bucket_name}")

    def upload_file(
        self, file_obj: BinaryIO, file_key: str, content_type: Optional[str] = None
    ) -> str:
        try:
            if not content_type:
                content_type = get_content_type(file_key)

            logger.info(f"📤 Uploading file to R2: {file_key}")

            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {"uploaded-by": "document-service"},
                },
            )

            file_url = f"{env.R2_PUBLIC_DOMAIN}/{file_key}"
            logger.info(f"✅ File uploaded successfully: {file_url}")

            return file_url

        except ClientError as e:
            error_msg = f"Failed to upload file to R2: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise R2StorageError(error_msg) from e

    def upload_text(
        self, text_content: str, file_key: str, content_type: str = "text/plain"
    ) -> str:
        try:
            logger.info(f"📤 Uploading text file to R2: {file_key}")

            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=text_content.encode("utf-8"),
                ContentType=f"{content_type}; charset=utf-8",
            )

            file_url = f"{env.R2_PUBLIC_DOMAIN}/{file_key}"
            logger.info(f"✅ Text file uploaded successfully: {file_url}")
            return file_url

        except ClientError as e:
            error_msg = f"Failed to upload text file to R2: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise R2StorageError(error_msg) from e

    def download_to_tempfile(self, file_key: str, prefix: str = "doc_") -> Path:
        try:
            logger.info(f"📥 Downloading file from R2: {file_key}")

            suffix = Path(file_key).suffix

            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix, prefix=prefix
            )

            self.client.download_fileobj(self.bucket_name, file_key, temp_file)

            temp_file.close()
            temp_path = Path(temp_file.name)

            logger.info(f"✅ File downloaded to: {temp_path}")
            return temp_path

        except ClientError as e:
            error_msg = f"Failed to download file from R2: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise R2StorageError(error_msg) from e

    def generate_presigned_url(
        self, file_key: str, expiration: int = env.PRESIGNED_URL_EXPIRATION
    ) -> str:
        try:
            logger.info(f"🔗 Generating presigned URL for: {file_key}")

            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_key},
                ExpiresIn=expiration,
            )

            logger.info(f"✅ Presigned URL generated (expires in {expiration}s)")
            return url

        except ClientError as e:
            error_msg = f"Failed to generate presigned URL: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise R2StorageError(error_msg) from e

    def delete_file(self, file_key: str) -> bool:
        try:
            logger.info(f"🗑️  Deleting file from R2: {file_key}")

            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)

            logger.info(f"✅ File deleted successfully: {file_key}")
            return True

        except ClientError as e:
            error_msg = f"Failed to delete file from R2: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise R2StorageError(error_msg) from e

    # def file_exists(self, file_key: str) -> bool:
    #     try:
    #         self.client.head_object(Bucket=self.bucket_name, Key=file_key)
    #         return True
    #     except ClientError:
    #         return False


r2_storage = R2StorageService()
