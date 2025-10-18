import boto3
from flask import current_app

def get_s3_base_url():
    """앱 실행 중 안전하게 S3 BASE URL을 반환"""
    bucket = current_app.config["S3_BUCKET"]
    region = current_app.config["S3_REGION"]
    return f"https://{bucket}.s3.{region}.amazonaws.com"


def s3_upload(file_path, s3_key, content_type):
    try:
        s3 = boto3.client("s3", region_name=current_app.config["S3_REGION"])
        bucket = current_app.config["S3_BUCKET"]

        s3.upload_file(
            file_path,
            bucket,
            s3_key,
            ExtraArgs={"ContentType": content_type}
        )
        print(f"✅ S3 업로드 완료: s3://{bucket}/{s3_key}")
    except Exception as e:
        print(f"⚠️ S3 업로드 실패 (무시): {e}")


def get_next_index(bucket, prefix):
    """S3에 저장된 파일 수 기반으로 다음 index 계산"""
    s3 = boto3.client("s3", region_name=current_app.config["S3_REGION"])
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" not in response:
            return 1
        return len(response["Contents"]) + 1
    except Exception as e:
        print(f"⚠️ S3 접근 실패: {e}")
        return 1