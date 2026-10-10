import boto3

from nyc_mobility.config import Settings

# ---------- object storage ----------

def get_s3_client(settings: Settings):
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",                  # required by boto3; object store ignores it
    )


def ensure_bucket(s3, bucket: str) -> None:
    existing = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if bucket not in existing:
        s3.create_bucket(Bucket=bucket)
        print(f"Created bucket: {bucket}")