import os

from b2sdk.v2 import B2Api, InMemoryAccountInfo, FileVersion


def upload_file(file: bytes, filename: str, content_type: str) -> str:
    info = InMemoryAccountInfo()
    b2 = B2Api(info)
    b2.authorize_account("production", os.getenv("B2_ID"), os.getenv("B2_KEY"))
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET"))
    res: FileVersion = bucket.upload_bytes(file, filename, content_type)
    return f"https://{os.getenv('B2_REGION')}.backblazeb2.com/file/{bucket.name}/{filename}"
