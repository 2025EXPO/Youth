# 카메라로 찍은 사진을 EC2에 저장하는 역할
# 프론트에서 전달받은 base64 이미지를 디코딩
# 날짜, 그룹명(img1), 순번(01~08)으로 파일명 지정
# /uploads 폴더에 저장
# 저장된 파일 경로(/uploads/1018_img1_01.jpg) 반환

from flask import Blueprint, request, jsonify
import base64, os
from datetime import datetime
from utils.file_utils import UPLOAD_DIR

capture_bp = Blueprint("capture", __name__)

@capture_bp.route("/capture", methods=["POST"])
def capture():
    try:
        data = request.get_json()
        img_data = data["image"]
        img_bytes = base64.b64decode(img_data.split(",")[1])

        date_str = datetime.now().strftime("%m%d")
        group_id = data.get("group", "img1")
        index = data.get("index", 1)
        filename = f"{date_str}_{group_id}_{int(index):02d}.jpg"

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(img_bytes)

        print(f"✅ 저장 완료: {filename}")
        return jsonify({"imageUrl": f"/uploads/{filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
