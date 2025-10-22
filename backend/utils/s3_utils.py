import boto3
from flask import current_app
import re

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
    # 숫자로 index 계산: 9 이후로도 인덱스 계산 가능하게 됨
    s3 = boto3.client("s3", region_name=current_app.config["S3_REGION"])
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" not in response:
            return 1

        numbers = []
        for obj in response["Contents"]:
            key = obj["Key"]
            match = re.search(r"(\d+)(?=\.\w+$)", key)
            if match:
                numbers.append(int(match.group(1)))

        return max(numbers) + 1 if numbers else 1

    except Exception as e:
        print(f"⚠️ S3 접근 실패: {e}")
        return 1

# 이전 코드
# def get_next_index(bucket, prefix):
#     """S3에 저장된 파일 수 기반으로 다음 index 계산"""
#     s3 = boto3.client("s3", region_name=current_app.config["S3_REGION"])
#     # try:
#         response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
#         if "Contents" not in response:
#             return 1
#         return len(response["Contents"]) + 1
#     except Exception as e:
#         print(f"⚠️ S3 접근 실패: {e}")
#         return 1