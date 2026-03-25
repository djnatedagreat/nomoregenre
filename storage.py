from utils import load_config

config = load_config()


def _s3_client():
    import boto3
    from botocore.config import Config
    endpoint_url = config.get("S3_ENDPOINT_URL")
    if not endpoint_url:
        raise Exception("S3_ENDPOINT_URL is not set in .env")
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=config.get("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=config.get("S3_SECRET_ACCESS_KEY"),
        region_name=config.get("S3_REGION"),
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'},
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )


class Storage:
    def __init__(self):
        self.bucket = config.get("S3_BACKUP_BUCKET")

    def upload_file(self, local_path, s3_key):
        """
        Uploads a local file to S3-compatible storage.
        s3_key is the destination path within the bucket (e.g. 'files/mix/filename.mp3')
        """
        if not self.bucket:
            raise Exception("S3_BACKUP_BUCKET is not set in .env")
        _s3_client().upload_file(local_path, self.bucket, s3_key)
        print(f"  Uploaded: {local_path} → s3://{self.bucket}/{s3_key}")

storage = Storage()
