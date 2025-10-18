from flask import Blueprint, request, jsonify, current_app
from utils.image_utils import combine_photos
from utils.s3_utils import s3_upload, get_next_index, get_s3_base_url 
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
        bucket = current_app.config["S3_BUCKET"]
        region = current_app.config["S3_REGION"]
        base_url = current_app.config["BASE_URL"]
        final_dir = current_app.config["FINAL_DIR"]

        # S3 인덱스 계산
        try:
            index = get_next_index(bucket, f"final/{date_prefix}_")
        except Exception as e:
            print(f"⚠️ S3 접근 실패: {e}")
            os.makedirs(final_dir, exist_ok=True)
            existing = [f for f in os.listdir(final_dir) if f.startswith(date_prefix)]
            index = len(existing) + 1

        output_filename = f"{date_prefix}_img{index}.png"

        # 디버깅 로그
        print("📸 받은 데이터:", photos)
        print("🎞 frame_key:", frame_key, "grayscale:", grayscale)
        print("💾 저장 파일명:", output_filename)

        # ✅ 4컷 합성 및 로컬 저장
        output_path = combine_photos(photos, frame_key, grayscale, output_filename)
        print(f"✅ 로컬 합성 완료: {output_path}")

        # ✅ S3 업로드 시도
        s3_key = f"final/{output_filename}"
        s3_url = f"{get_s3_base_url()}/final/{output_filename}" #여기
        try:
            s3_upload(output_path, s3_key, "image/png")
            print(f"✅ S3 업로드 성공: {s3_url}")
            return jsonify({"url": s3_url})
        except Exception as s3_error:
            print(f"⚠️ S3 업로드 실패 (무시): {s3_error}")

        # ✅ 로컬 URL 반환 (S3 실패 시)
        local_url = f"{base_url}/final/{output_filename}"
        print(f"📂 로컬 URL 반환: {local_url}")
        return jsonify({"url": local_url})

    except Exception as e:
        print("❌ /final 처리 중 오류 발생:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
