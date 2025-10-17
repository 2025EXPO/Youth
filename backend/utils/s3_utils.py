# AWS S3 업로드 및 파일 관리 유틸
# s3_upload() → 로컬 파일을 지정된 Key에 업로드
# get_next_index() → prefix 기준으로 S3 파일 개수 세서 다음 인덱스 자동 계산
# S3_BUCKET, S3_REGION, S3_BASE_URL 설정

import boto3

S3_BUCKET = "expo-2025-s3"
S3_REGION = "ap-northeast-3"
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"
s3 = boto3.client("s3", region_name=S3_REGION)

def s3_upload(local_path, key, content_type):
    with open(local_path, "rb") as f:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=f,
            ContentType=content_type,
            ACL="public-read"
        )

def get_next_index(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    count = len(response.get("Contents", []))
    return count + 1
