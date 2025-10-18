# AWS S3 업로드 및 파일 관리 유틸
# s3_upload() → 로컬 파일을 지정된 Key에 업로드
# get_next_index() → prefix 기준으로 S3 파일 개수 세서 다음 인덱스 자동 계산
# S3_BUCKET, S3_REGION, S3_BASE_URL 설정
import boto3
from flask import current_app

def s3_upload(file_path, s3_key, content_type):
    try:
        s3 = boto3.client("s3", region_name=current_app.config["S3_REGION"])
        bucket = current_app.config["S3_BUCKET"]

        s3.upload_file(file_path, bucket, s3_key, ExtraArgs={"ContentType": content_type})
 
        print(f"✅ S3 업로드 완료: s3://{bucket}/{s3_key}")
    except Exception as e:
        print(f"⚠️ S3 업로드 실패 (무시): {e}")

def get_next_index(bucket, prefix): # 파일명인덱스
    s3 = boto3.client("s3", region_name=current_app.config["S3_REGION"])
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" not in response:
            return 1
        return len(response["Contents"]) + 1
    except Exception as e:
        print(f"⚠️ S3 접근 실패: {e}")
        return 1

S3_BASE_URL = f"https://{current_app.config['S3_BUCKET']}.s3.{current_app.config['S3_REGION']}.amazonaws.com"