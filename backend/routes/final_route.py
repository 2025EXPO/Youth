from flask import Blueprint, request, jsonify
from utils.s3_utils import s3_upload, get_next_index, S3_BASE_URL, S3_BUCKET
from utils.image_utils import combine_photos
from datetime import datetime
import os, traceback

final_bp = Blueprint("final", __name__)

@final_bp.route("/final", methods=["POST"])
def final():
    try:
        data = request.get_json()
        photos = data.get("photos", [])
        frame_key = data.get("frameKey", "frame1")
        grayscale = data.get("grayscale", False)

        date_prefix = datetime.now().strftime("%m%d")

        # S3 접근 안되면 ec2에 저장
        try:
            index = get_next_index(S3_BUCKET, f"final/{date_prefix}_")
        except Exception as e:
            print(f"⚠️ S3 접근 실패: {e}")
            # 로컬 final 폴더 기준으로 인덱스 계산
            FINAL_DIR = os.path.join(os.getcwd(), "final")
            os.makedirs(FINAL_DIR, exist_ok=True)
            existing = [f for f in os.listdir(FINAL_DIR) if f.startswith(date_prefix)]
            index = len(existing) + 1

        output_filename = f"{date_prefix}_img{index}.png"

        # 디버깅 로그
        print("📸 받은 데이터:", photos)
        print("🎞 frame_key:", frame_key, "grayscale:", grayscale)
        print("💾 저장 파일명:", output_filename)

        # 4컷 합성 및 로컬 저장
        output_path = combine_photos(photos, frame_key, grayscale, output_filename)
        print(f"✅ 로컬 합성 완료: {output_path}")

        # S3 업로드
        try:
            s3_upload(output_path, f"final/{output_filename}", "image/png")
            s3_url = f"{S3_BASE_URL}/final/{output_filename}"
            print(f"✅ S3 업로드 성공: {s3_url}")
        except Exception as s3_error:
            print(f"⚠️ S3 업로드 실패 (무시): {s3_error}")
            s3_url = None

        # 응답 -S3 없으면 EC2 경로 반환
        if s3_url:
            return jsonify({"url": s3_url})
        else:
            local_url = f"http://13.208.215.216:5000/final/{output_filename}"
            return jsonify({"url": local_url})

    except Exception as e:
        print("❌ /final 처리 중 오류 발생:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
