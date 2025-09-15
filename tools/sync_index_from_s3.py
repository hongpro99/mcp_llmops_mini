# tools/sync_index_from_s3.py
import os
import boto3
import pathlib

def main():
    bucket = os.environ.get("S3_BUCKET", "my-mini-rag-vectors")
    prefix = os.environ.get("S3_PREFIX", "prod/faiss_index")
    local_dir = os.environ.get("VECTOR_DIR", "/app/vectorstore/faiss_index")

    print(f"[sync_index_from_s3] bucket={bucket}, prefix={prefix} → {local_dir}")

    s3 = boto3.client("s3")
    pathlib.Path(local_dir).mkdir(parents=True, exist_ok=True)

    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" not in resp:
        print("[sync_index_from_s3] no objects found in S3")
        return

    for obj in resp["Contents"]:
        key = obj["Key"]
        if key.endswith("/"):  # prefix 디렉토리라면 skip
            continue
        rel_path = key.replace(prefix, "").lstrip("/")
        local_path = os.path.join(local_dir, rel_path)

        pathlib.Path(os.path.dirname(local_path)).mkdir(parents=True, exist_ok=True)
        print(f"[sync_index_from_s3] downloading {key} → {local_path}")
        s3.download_file(bucket, key, local_path)

    print("[sync_index_from_s3] done!")

if __name__ == "__main__":
    main()
