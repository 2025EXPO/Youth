# 4컷 합성 → S3 업로드 담당
# /capture로 찍힌 8장의 사진 중 선택된 4장을 합성
# 선택된 프레임(frame1~frame5)에 맞게 좌표 계산
# 로컬 /final에 저장 후,
# S3 final/1018_img1.png 경로로 업로드
# S3 URL 반환 → QR 코드로 사용 가능

from flask import Blueprint, request, jsonify
from utils.s3_utils import s3_upload, get_next_index, S3_BASE_URL, S3_BUCKET
from utils.image_utils import combine_photos
from datetime import datetime
import os

final_bp = Blueprint("final", __name__)

@final_bp.route("/final", methods=["POST"])
def final():
    try:
        data = request.get_json()
        photos = data.get("photos", [])
        frame_key = data.get("frameKey", "frame1")
        grayscale = data.get("grayscale", False)

        date_prefix = datetime.now().strftime("%m%d")
        index = get_next_index(S3_BUCKET, f"final/{date_prefix}_")
        output_filename = f"{date_prefix}_img{index}.png"
        output_path = combine_photos(photos, frame_key, grayscale, output_filename)

        s3_upload(output_path, f"final/{output_filename}", "image/png")
        s3_url = f"{S3_BASE_URL}/final/{output_filename}"

        print(f"✅ /final 업로드 완료: {s3_url}")
        return jsonify({"url": s3_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
