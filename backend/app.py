# app.py
import os
import base64
import uuid
from flask import Flask, request, jsonify, send_from_directory
from print_utils import make_print_pdf, print_pdf   
from flask_cors import CORS
from PIL import Image, ImageOps

app = Flask(__name__)
CORS(app)

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAME_DIR = os.path.join(BASE_DIR, "frames")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FINAL_DIR = os.path.join(BASE_DIR, "final")
PRINT_DIR = os.path.join(BASE_DIR, "print")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(PRINT_DIR, exist_ok=True)


# === 1️⃣ 사진 업로드 (base64 저장) ===
@app.route("/capture", methods=["POST"])
def capture():
    try:
        data = request.get_json()
        img_data = data["image"]
        img_bytes = base64.b64decode(img_data.split(",")[1])

        filename = f"{uuid.uuid4()}.jpg"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(img_bytes)

        return jsonify({"imageUrl": f"/uploads/{filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === 2️⃣ 4장 + 프레임 합성 ===
@app.route("/final", methods=["POST"])
def final():
    import json
    from PIL import Image, ImageOps

    try:
        print("===== /final 요청 도착 =====")
        data = request.get_json()
        print("요청 데이터:", data)

        photos = data.get("photos", [])
        grayscale = data.get("grayscale", False)
        frame_key = data.get("frameKey", "frame1")

        # 🔹 프레임 매핑
        frame_map = {
            "frame1": "WhiteRound.png",
            "frame2": "BlackRound.png",
            "frame3": "PartyRound.png",
            "frame4": "ZebraRound.png",
            "frame5": "Shingu.png",
            "special1": "StarRound.png",
            "special2": "OceanRound.png",
            "special3": "ShinguFunny.png",
            "DenimFrame": "DenimFrame.png",
        }

        frame_filename = frame_map.get(frame_key, "WhiteRound.png")
        frame_path = os.path.join(FRAME_DIR, frame_filename)
        if not os.path.exists(frame_path):
            print("❌ 프레임 파일 없음:", frame_path)
            return jsonify({"error": f"Frame not found: {frame_path}"}), 400

        frame = Image.open(frame_path).convert("RGBA")
        frame_w, frame_h = frame.size
        print(f"✅ 프레임 로드 완료: {frame_path}")
        print(f"프레임 크기: {frame_w}x{frame_h}")

        # ✅ 모든 프레임 공통 좌표
        # 기준: 프레임 크기 592.67×1778
        # x = 23.71, w = 545.24, h = 344.73
        # y = 29.63 / 393.13 / 756.63 / 1120.13
        base_positions = [
            {"x": 23.71 / 592.67, "y": 29.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
            {"x": 23.71 / 592.67, "y": 393.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
            {"x": 23.71 / 592.67, "y": 756.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
            {"x": 23.71 / 592.67, "y": 1120.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        ]
        # # ✅ 새 프레임 크기 572×1700 기준
        # base_positions = [
        #     {"x": 22.88 / 572, "y": 28.33 / 1700, "w": 526.76 / 572, "h": 329.51 / 1700},
        #     {"x": 22.88 / 572, "y": 375.22 / 1700, "w": 526.76 / 572, "h": 329.51 / 1700},
        #     {"x": 22.88 / 572, "y": 723.34 / 1700, "w": 526.76 / 572, "h": 329.51 / 1700},
        #     {"x": 22.88 / 572, "y": 1071.45 / 1700, "w": 526.76 / 572, "h": 329.51 / 1700},
        # ]

               

        # ✅ 프레임별 좌표 설정 (전부 동일 구조)
        frame_positions_percent = {
            "WhiteRound.png": base_positions,
            "BlackRound.png": base_positions,
            "PartyRound.png": base_positions,
            "ZebraRound.png": base_positions,
            "Shingu.png": base_positions,
            "StarRound.png": base_positions,
            "OceanRound.png": base_positions,
            "ShinguFunny.png": base_positions,
            "DenimFrame.png": base_positions,
        }

        percents = frame_positions_percent.get(frame_filename)
        if not percents:
            print(f"❌ '{frame_filename}'에 대한 좌표 정의 없음")
            return jsonify({"error": "좌표 정의가 없습니다."}), 400

        # ✅ 퍼센트 → 실제 px 변환
        positions = [
            {
                "x": int(p["x"] * frame_w),
                "y": int(p["y"] * frame_h),
                "width": int(p["w"] * frame_w),
                "height": int(p["h"] * frame_h),
            }
            for p in percents
        ]

        print("📐 변환된 실제 positions:", positions)

        # 🔹 사진 합성
        for i, photo_url in enumerate(photos):
            if i >= len(positions):
                break
            pos = positions[i]
            photo_path = photo_url.replace("/uploads/", f"{UPLOAD_DIR}/")
            if not os.path.exists(photo_path):
                print(f"❌ 사진 파일 없음: {photo_path}")
                continue

            img = Image.open(photo_path).convert("RGBA").resize(
                (pos["width"], pos["height"])
            )
            if grayscale:
                img = ImageOps.grayscale(img).convert("RGBA")

            frame.paste(img, (pos["x"], pos["y"]), img)
            print(f"✅ 사진 {i+1} 합성 완료")

        # 🔹 결과 저장
        output_filename = f"final_{uuid.uuid4()}.png"
        output_path = os.path.join(FINAL_DIR, output_filename)
        frame.save(output_path)
        print("✅ 최종 합성 완료:", output_path)

        return jsonify({"url": f"/final/{output_filename}"})

    except Exception as e:
        print("❌ /final 처리 중 오류 발생:", e)
        return jsonify({"error": str(e)}), 500




# === 3️⃣ 인쇄용: 두 장 나란히 붙이기 + 자동 프린트 ===
@app.route("/print", methods=["POST"])
def print_ready():
    try:
        data = request.get_json()
        final_url = data["url"]
        final_path = final_url.replace("/final/", f"{FINAL_DIR}/")

        print(f"📂 인쇄 요청: {final_url}")

        # ✅ PDF 생성
        pdf_path = make_print_pdf(final_path)

        # ✅ 인쇄 명령 전송
        print_pdf(pdf_path)

        # ✅ 클라이언트 반환
        filename = os.path.basename(pdf_path)
        return jsonify({"url": f"/print/{filename}"})

    except Exception as e:
        print("❌ /print 처리 중 오류:", e)
        return jsonify({"error": str(e)}), 500




# === 정적 파일 서빙 ===
@app.route("/uploads/<filename>")
def serve_uploads(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/final/<filename>")
def serve_final(filename):
    return send_from_directory(FINAL_DIR, filename)

@app.route("/print/<filename>")
def serve_print(filename):
    return send_from_directory(PRINT_DIR, filename)


# === 서버 상태 체크 ===
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

