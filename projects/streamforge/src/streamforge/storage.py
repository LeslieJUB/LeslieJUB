import json
from datetime import UTC, datetime
from io import BytesIO

import boto3
import pandas as pd
from botocore.config import Config

from .config import get_settings


def s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        aws_access_key_id=settings.s3_access_key if settings.s3_endpoint_url else None,
        aws_secret_access_key=settings.s3_secret_key if settings.s3_endpoint_url else None,
        region_name=settings.s3_region,
        config=Config(s3={"addressing_style": "path"}),
    )


def write_batch(records: list[dict]) -> dict[str, str]:
    if not records:
        return {}
    settings = get_settings()
    client = s3_client()
    now = datetime.now(UTC)
    partition = now.strftime("year=%Y/month=%m/day=%d/hour=%H")
    stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    bronze_key = f"bronze/orders/{partition}/batch-{stamp}.jsonl"
    silver_key = f"silver/orders/{partition}/batch-{stamp}.parquet"
    raw = "\n".join(json.dumps(row, default=str) for row in records).encode()
    client.put_object(
        Bucket=settings.s3_bucket_bronze,
        Key=bronze_key,
        Body=raw,
        ContentType="application/x-ndjson",
    )
    frame = pd.DataFrame(records)
    parquet = BytesIO()
    frame.to_parquet(parquet, index=False, engine="pyarrow", compression="snappy")
    client.put_object(
        Bucket=settings.s3_bucket_silver,
        Key=silver_key,
        Body=parquet.getvalue(),
        ContentType="application/vnd.apache.parquet",
    )
    return {"bronze": bronze_key, "silver": silver_key}
