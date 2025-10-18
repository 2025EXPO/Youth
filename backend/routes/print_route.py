from flask import Blueprint, request, jsonify, current_app
from utils.print_utils import make_print_pdf
from utils.s3_utils import s3_upload, get_next_index
from datetime import datetime
import os, traceback

print_bp = Blueprint("print", __name__)

@print_bp.route("/print", methods=["POST"])
def print_ready():
    try:
        data = request.get_json()
        final_url = data.get("url")
        if not final_url:
            return jsonify({"error": "final_url 누락"}), 400

        # ✅ Config 값 불러오기
        base_url = current_app.config["BASE_URL"]
        final_dir = current_app.config["FINAL_DIR"]
        print_dir = current_app.config["PRINT_DIR"]
        bucket = current_app.config["S3_BUCKET"]
        region = current_app.config["S3_REGION"]

        # ✅ 최종 이미지 경로 확인
        filename = os.path.basename(final_url)
        final_path = os.path.join(final_dir, filename)
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"최종 이미지가 없습니다: {final_path}")

        # ✅ PDF 생성
        pdf_path = make_print_pdf(final_path)
        print(f"🖨️ PDF 생성 완료: {pdf_path}")

        # ✅ S3 업로드 시도
        s3_url = None
        try:
            date_prefix = datetime.now().strftime("%m%d")
            index = get_next_index(bucket, f"print/{date_prefix}_")
            s3_key = f"print/{date_prefix}_img{index}.pdf"
            s3_upload(pdf_path, s3_key, "application/pdf")
            s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
            print(f"✅ S3 업로드 완료: {s3_url}")
        except Exception as s3_err:
            print(f"⚠️ S3 업로드 실패 (무시): {s3_err}")

        # ✅ 응답 생성
        return jsonify({
            "pdf_path": pdf_path,
            "s3_url": s3_url or f"{base_url}/print/{os.path.basename(pdf_path)}"
        })

    except Exception as e:
        print("❌ /print 처리 중 오류 발생:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
