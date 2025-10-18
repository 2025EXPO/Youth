from flask import Blueprint, request, jsonify
from utils.print_utils import make_print_pdf
from utils.s3_utils import s3_upload, get_next_index, S3_BASE_URL, S3_BUCKET
from datetime import datetime
import os
import traceback

print_bp = Blueprint("print", __name__)

@print_bp.route("/print", methods=["POST"])
def print_ready():
    try:
        data = request.get_json()
        final_url = data.get("url")
        if not final_url:
            return jsonify({"error": "final_url 누락"}), 400

        filename = os.path.basename(final_url)

        # 절대경로
        final_path = os.path.join(os.getcwd(), "final", filename)
        if not os.path.exists(final_path):
            raise FileNotFoundError(f"최종 이미지가 없습니다: {final_path}")

        # PDF 생성
        pdf_path = make_print_pdf(final_path)
        print(f"🖨️ PDF 생성 완료: {pdf_path}")

        # S3 업로드 시도
        try:
            date_prefix = datetime.now().strftime("%m%d")
            index = get_next_index(S3_BUCKET, f"print/{date_prefix}_")
            s3_key = f"print/{date_prefix}_img{index}.pdf"
            s3_upload(pdf_path, s3_key, "application/pdf")
            s3_url = f"{S3_BASE_URL}/{s3_key}"
            print(f"✅ S3 업로드 완료: {s3_url}")
        except Exception as s3_err:
            print(f"⚠️ S3 업로드 실패 (무시): {s3_err}")
            s3_url = None

        # EC2에 저장된 PDF 경로 반환
        return jsonify({
            "pdf_path": pdf_path,
            "s3_url": s3_url or "(S3 업로드 실패 - 로컬 경로에 반환됨)"
        })

    except Exception as e:
        print("❌ /print 처리 중 오류 발생:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
