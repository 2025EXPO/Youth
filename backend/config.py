import os

class Config:
    # 서버 기본
    current_ip="56.155.45.183"
    BASE_URL = f"http://{current_ip}:5000"
    DEBUG = True

    # AWS S3 설정
    S3_BUCKET = "expo-2025-s3"
    S3_REGION = "ap-northeast-3"

    # 디렉토리 경로 설정
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    FRAME_DIR = os.path.join(BASE_DIR, "frames")
    FINAL_DIR = os.path.join(BASE_DIR, "final")
    PRINT_DIR = os.path.join(BASE_DIR, "print")

# class DevelopmentConfig(Config):
#     """로컬 테스트용"""
#     DEBUG = True

# class ProductionConfig(Config):
#     """EC2 등 실제 배포용"""
#     DEBUG = False
