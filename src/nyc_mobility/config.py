import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    pipeline_env: str

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str

    tlc_dataset: str
    tlc_month: str

    @property
    def postgres_dsn(self) -> str:
        """Connection string for Postgres."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @classmethod
    def from_env(cls) -> "Settings":
        """Build Settings from environment variables. Fails fast if required ones are missing."""
        return cls(
            pipeline_env=os.getenv("PIPELINE_ENV", "local"),
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_user=os.environ["POSTGRES_USER"],
            postgres_password=os.environ["POSTGRES_PASSWORD"],
            postgres_db=os.environ["POSTGRES_DB"],
            s3_endpoint_url=os.environ["S3_ENDPOINT_URL"],
            s3_access_key=os.environ["S3_ACCESS_KEY"],
            s3_secret_key=os.environ["S3_SECRET_KEY"],
            s3_bucket=os.environ["S3_BUCKET"],
            tlc_dataset=os.getenv("TLC_DATASET", "yellow_tripdata"),
            tlc_month=os.getenv("TLC_MONTH", "2024-01"),
        )