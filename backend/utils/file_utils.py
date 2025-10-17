# 로컬 폴더 경로와 초기화 담당
# BASE_DIR, UPLOAD_DIR, FINAL_DIR, PRINT_DIR, FRAME_DIR 경로 정의
# 폴더 자동 생성 (os.makedirs(..., exist_ok=True))

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FINAL_DIR = os.path.join(BASE_DIR, "final")
PRINT_DIR = os.path.join(BASE_DIR, "print")
FRAME_DIR = os.path.join(BASE_DIR, "frames")

for path in [UPLOAD_DIR, FINAL_DIR, PRINT_DIR]:
    os.makedirs(path, exist_ok=True)
