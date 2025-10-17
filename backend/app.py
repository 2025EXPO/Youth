# Flask 진입점
# routes/ 폴더에 있는 각 기능별 /capture, /final, /print, /health 라우트를 Flask에 연결

from flask import Flask
from flask_cors import CORS
from routes.capture_route import capture_bp
from routes.final_route import final_bp
from routes.print_route import print_bp
from routes.health_route import health_bp

app = Flask(__name__)
CORS(app)

# 모듈 등록
app.register_blueprint(capture_bp)
app.register_blueprint(final_bp)
app.register_blueprint(print_bp)
app.register_blueprint(health_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



# import boto3
# import os
# import base64
# import uuid
# from datetime import datetime
# from flask import Flask, request, jsonify
# from print_utils import make_print_pdf, print_pdf
# from flask_cors import CORS
# from PIL import Image, ImageOps

# app = Flask(__name__)
# CORS(app)

# # === AWS S3 설정 ===
# S3_BUCKET = "expo-2025-s3"
# S3_REGION = "ap-northeast-3"
# S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"
# s3 = boto3.client("s3", region_name=S3_REGION)

# # === 로컬 폴더 (임시 저장용) ===
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FRAME_DIR = os.path.join(BASE_DIR, "frames")
# UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
# FINAL_DIR = os.path.join(BASE_DIR, "final")
# PRINT_DIR = os.path.join(BASE_DIR, "print")

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(FINAL_DIR, exist_ok=True)
# os.makedirs(PRINT_DIR, exist_ok=True)

# # === 날짜별 prefix 자동 생성 ===
# def get_today_prefix():
#     return datetime.now().strftime("%m%d")  # 예: "1018"

# # === 현재 prefix(폴더) 내 파일 개수를 세고 다음 번호 반환 ===
# def get_next_index(bucket, prefix):
#     response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
#     count = 0
#     if "Contents" in response:
#         count = len(response["Contents"])
#     return count + 1


# # === 1️⃣ /capture : base64 사진 업로드 → S3 uploads/1018_img{n}_{n}.jpg ===
# @app.route("/capture", methods=["POST"])
# def capture():
#     try:
#         data = request.get_json()
#         img_data = data["image"]
#         img_bytes = base64.b64decode(img_data.split(",")[1])

#         # ✅ 오늘 날짜 (예: 1018)
#         date_str = datetime.now().strftime("%m%d")

#         # ✅ 그룹 번호(프론트에서 받아올 수도 있음)
#         # 프론트에서 예: ?group=img1 형태로 보내도 되고,
#         # 일단 기본값은 img1로 설정
#         group_id = data.get("group", "img1")

#         # ✅ 현재 사진 순번 (프론트에서 count 같이 보내면 좋음)
#         photo_index = data.get("index", 1)
#         photo_index_str = f"{int(photo_index):02d}"  # 1 → 01

#         # ✅ 최종 파일명
#         filename = f"{date_str}_{group_id}_{photo_index_str}.jpg"

#         path = os.path.join(UPLOAD_DIR, filename)
#         with open(path, "wb") as f:
#             f.write(img_bytes)

#         print(f"✅ 저장 완료: {filename}")

#         return jsonify({"imageUrl": f"/uploads/{filename}"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# # === 2️⃣ /final : 4장 합성 → S3 final/1018_img{n}.png ===
# @app.route("/final", methods=["POST"])
# def final():
#     try:
#         data = request.get_json()
#         photos = data.get("photos", [])
#         grayscale = data.get("grayscale", False)
#         frame_key = data.get("frameKey", "frame1")

#         # 프레임 매핑
#         frame_map = {
#             "frame1": "WhiteRound.png",
#             "frame2": "BlackRound.png",
#             "frame3": "PartyRound.png",
#             "frame4": "ZebraRound.png",
#             "frame5": "Shingu.png",
#             "special1": "StarRound.png",
#             "special2": "OceanRound.png",
#             "special3": "ShinguFunny.png",
#             "DenimFrame": "DenimFrame.png",
#         }

#         frame_filename = frame_map.get(frame_key, "WhiteRound.png")
#         frame_path = os.path.join(FRAME_DIR, frame_filename)
#         frame = Image.open(frame_path).convert("RGBA")
#         frame_w, frame_h = frame.size

#         # 좌표
#         base_positions = [
#             {"x": 23.71 / 592.67, "y": 29.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
#             {"x": 23.71 / 592.67, "y": 393.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
#             {"x": 23.71 / 592.67, "y": 756.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
#             {"x": 23.71 / 592.67, "y": 1120.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
#         ]

#         positions = [
#             {
#                 "x": int(p["x"] * frame_w),
#                 "y": int(p["y"] * frame_h),
#                 "width": int(p["w"] * frame_w),
#                 "height": int(p["h"] * frame_h),
#             }
#             for p in base_positions
#         ]

#         # 사진 합성
#         for i, photo_url in enumerate(photos):
#             if i >= len(positions):
#                 break
#             pos = positions[i]
#             filename = os.path.basename(photo_url)
#             local_photo_path = os.path.join(UPLOAD_DIR, filename)
#             if not os.path.exists(local_photo_path):
#                 continue

#             img = Image.open(local_photo_path).convert("RGBA").resize(
#                 (pos["width"], pos["height"])
#             )
#             if grayscale:
#                 img = ImageOps.grayscale(img).convert("RGBA")

#             frame.paste(img, (pos["x"], pos["y"]), img)

#         # ✅ 파일명 자동 생성
#         date_prefix = get_today_prefix()
#         prefix = f"final/{date_prefix}_"
#         index = get_next_index(S3_BUCKET, prefix)
#         output_filename = f"{date_prefix}_img{index}.png"
#         output_path = os.path.join(FINAL_DIR, output_filename)
#         frame.save(output_path)

#         # ✅ S3 업로드
#         s3_key = f"final/{output_filename}"
#         with open(output_path, "rb") as f:
#             s3.put_object(
#                 Bucket=S3_BUCKET,
#                 Key=s3_key,
#                 Body=f,
#                 ContentType="image/png",
#                 ACL="public-read"
#             )

#         s3_url = f"{S3_BASE_URL}/{s3_key}"
#         print(f"✅ /final 업로드 완료: {s3_url}")

#         return jsonify({"url": s3_url, "index": index})

#     except Exception as e:
#         print("❌ /final 오류:", e)
#         return jsonify({"error": str(e)}), 500


# # === 3️⃣ /print : PDF 생성 → S3 print/1018_img{n}.pdf ===
# @app.route("/print", methods=["POST"])
# def print_ready():
#     try:
#         data = request.get_json()
#         final_url = data["url"]
#         local_final_path = os.path.join(FINAL_DIR, os.path.basename(final_url))

#         # PDF 생성
#         pdf_path = make_print_pdf(local_final_path)

#         # ✅ 파일명 자동 생성
#         date_prefix = get_today_prefix()
#         prefix = f"print/{date_prefix}_"
#         index = get_next_index(S3_BUCKET, prefix)
#         filename = f"{date_prefix}_img{index}.pdf"

#         # ✅ S3 업로드
#         s3_key = f"print/{filename}"
#         with open(pdf_path, "rb") as f:
#             s3.put_object(
#                 Bucket=S3_BUCKET,
#                 Key=s3_key,
#                 Body=f,
#                 ContentType="application/pdf",
#                 ACL="public-read"
#             )

#         s3_url = f"{S3_BASE_URL}/{s3_key}"
#         print(f"✅ /print 업로드 완료: {s3_url}")

#         return jsonify({"url": s3_url})

#     except Exception as e:
#         print("❌ /print 오류:", e)
#         return jsonify({"error": str(e)}), 500


# # === 서버 상태 ===
# @app.route("/health")
# def health():
#     return jsonify({"status": "ok"})


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
