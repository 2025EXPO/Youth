# 인쇄용 PDF 생성 + S3 업로드
# /final에서 생성된 최종 이미지(S3 URL) 입력받음
# 그 이미지를 이용해 PDF 생성 (make_print_pdf())
# PDF를 S3 print/ 폴더로 업로드 (print/1018_img1.pdf)
# 인쇄 명령 전송(옵션) + PDF URL 반환

from flask import Blueprint, request, jsonify
from backend.utils.print_utils import make_print_pdf
from utils.s3_utils import s3_upload, get_next_index, S3_BASE_URL, S3_BUCKET
from datetime import datetime
import os

print_bp = Blueprint("print", __name__)

@print_bp.route("/print", methods=["POST"])
def print_ready():
    try:
        data = request.get_json()
        final_url = data["url"]
        filename = os.path.basename(final_url)
        pdf_path = make_print_pdf(os.path.join("final", filename))

        date_prefix = datetime.now().strftime("%m%d")
        index = get_next_index(S3_BUCKET, f"print/{date_prefix}_")
        s3_key = f"print/{date_prefix}_img{index}.pdf"

        s3_upload(pdf_path, s3_key, "application/pdf")
        s3_url = f"{S3_BASE_URL}/{s3_key}"

        return jsonify({"url": s3_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
