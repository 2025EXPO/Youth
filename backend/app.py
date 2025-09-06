# 필요한 라이브러리들을 가져옵니다.
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS, cross_origin
import base64
import os
import uuid
import io, requests
from PIL import Image, ImageOps

# Flask 앱을 생성합니다.
app = Flask(__name__)
# 개발용: 모든 출처 허용 (나중에 S3 배포 시 화이트리스트로 좁히세요)
CORS(app, resources={r"/*": {"origins": "*"}})

# 현재 파일(app.py)이 있는 폴더의 절대 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 사진을 저장할 폴더를 절대 경로로 지정합니다.
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 프레임+ 선택4장의 최종네컷을 저장할 경로
FINALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'finals')
os.makedirs(FINALS_FOLDER, exist_ok=True)

# 프레임 PNG 매핑 (경로는 실제 파일 위치에 맞춰 두세요)
FRAME_MAP = {
    # Round 타입
    "frame1": os.path.join(BASE_DIR, "templates", "frames", "WhiteRound.png"),
    "frame2": os.path.join(BASE_DIR, "templates", "frames", "BlackRound.png"),
    "frame3": os.path.join(BASE_DIR, "templates", "frames", "PartyRound.png"),
    "frame4": os.path.join(BASE_DIR, "templates", "frames", "ZebraRound.png"),
    "frame5": os.path.join(BASE_DIR, "templates", "frames", "Shingu.png"),

    # Text 타입 (필요하면 사용)
    "frame6": os.path.join(BASE_DIR, "templates", "frames", "WhiteText.png"),
    "frame7": os.path.join(BASE_DIR, "templates", "frames", "BlackText.png"),
    "frame8": os.path.join(BASE_DIR, "templates", "frames", "PartyText.png"),
    "frame9": os.path.join(BASE_DIR, "templates", "frames", "ZebraText.png"),
    "frame10": os.path.join(BASE_DIR, "templates", "frames", "Shingu.png"),

    # Special 타입 (필요하면 사용)
    "special1": os.path.join(BASE_DIR, "templates", "frames", "StarRound.png"),
    "special2": os.path.join(BASE_DIR, "templates", "frames", "OceanRound.png"),
    "special3": os.path.join(BASE_DIR, "templates", "frames", "ShinguFunny.png"),
}

# =========================
# 유틸 함수
# =========================

# URL → PIL.Image (메모리 변환)
def _open_url(url: str) -> Image.Image:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")

# 1열 4컷 (2×6inch / 600×1800) + 프레임 오버레이
def make_4cut(photo_urls, frame_path=None, grayscale=False) -> Image.Image:
    if not frame_path or not os.path.exists(frame_path):
        raise ValueError(f"Frame not found: {frame_path}")

    # 프레임(바깥마진 포함 616x1800) 기준 캔버스
    frame_rgba = Image.open(frame_path).convert("RGBA")
    W, H = frame_rgba.size  # 기대: 616 x 1800
    canvas = Image.new("RGBA", (W, H), "white")

    imgs = [_open_url(u) for u in photo_urls]
    if grayscale:
        imgs = [ImageOps.grayscale(im).convert("RGB") for im in imgs]

    # 내부 프레임 원점(0,0) 기준 슬롯 좌표
    inner_positions = [(23, 29), (23, 393), (23, 756), (23, 1121)]
    SLOT_W, SLOT_H = 546, 345
    SLOT_AR = 16 / 10

    # 좌우 바깥 마진 (프레임 PNG에 포함된 투명 여백)
    LEFT_MARGIN = 12  # 오른쪽도 12라면 PNG 폭 616 = 12 + 592 + 12

    try:
        RESAMPLE = Image.Resampling.LANCZOS
    except AttributeError:
        RESAMPLE = Image.LANCZOS

    for im, (ix, iy) in zip(imgs, inner_positions):
        # 슬롯 박스(SLOT_W x SLOT_H) 안에 16:10을 최대 크기로 맞춤 (cover)
        tw = SLOT_W
        th = int(round(tw / SLOT_AR))
        if th > SLOT_H:
            th = SLOT_H
            tw = int(round(th * SLOT_AR))

        fitted = ImageOps.fit(im, (tw, th), method=RESAMPLE, centering=(0.5, 0.5)).convert("RGBA")

        # 실제 캔버스 좌표 = 좌측 바깥마진 + 내부좌표 + 슬롯 내 중앙정렬 보정
        px = LEFT_MARGIN + ix + (SLOT_W - tw) // 2
        py = iy + (SLOT_H - th) // 2
        canvas.paste(fitted, (px, py), fitted)

    combined = Image.alpha_composite(canvas, frame_rgba)
    return combined.convert("RGB")

# 프린트용: 1200×1800에 동일 스트립 2장 좌/우 배치
def make_print(strip: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (1200, 1800), "white")
    canvas.paste(strip, (0, 0))
    canvas.paste(strip, (600, 0))
    return canvas

# =========================
# 라우트
# =========================

@app.route('/')
def home():
    return "백엔드 서버가 작동 중입니다. /test 로 이동하여 테스트하세요."

@app.route('/test')
def test_page():
    return render_template('test_capture.html')

# 촬영 저장
@app.route('/capture', methods=['POST'])
@cross_origin(origins="*")
def capture():
    if not request.is_json:
        return jsonify({"message": "요청 형식이 JSON이 아닙니다."}), 400

    data = request.get_json()
    if 'image' not in data:
        return jsonify({"message": "'image' 키가 요청에 없습니다."}), 400

    image_data = data['image']

    try:
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)

        original_filename = f"{uuid.uuid4()}_original.jpg"
        original_filepath = os.path.join(UPLOAD_FOLDER, original_filename)
        with open(original_filepath, "wb") as f:
            f.write(binary_data)

        image = Image.open(original_filepath)
        border_size = 20
        decorated_image = ImageOps.expand(image, border=border_size, fill='black')

        decorated_filename = f"{uuid.uuid4()}_decorated.jpg"
        decorated_filepath = os.path.join(UPLOAD_FOLDER, decorated_filename)
        decorated_image.save(decorated_filepath)

        # 외부접속 가능한 호스트로 반환 (127.0.0.1 제거)
        from urllib.parse import urljoin
        image_url = urljoin(request.host_url, f"images/{decorated_filename}")

        return jsonify({
            'message': '사진 처리 및 저장이 완료되었습니다.',
            'imageUrl': image_url
        }), 200

    except Exception as e:
        print(f"!!! 서버 내부 오류 발생: {e}")
        return jsonify({'message': '사진 처리 중 서버 내부에서 오류가 발생했습니다.', 'error': str(e)}), 500

# 최종본 생성 (QR용)
@app.route("/final", methods=["POST", "OPTIONS"])
@cross_origin(origins="*")
def make_final():
    if request.method == "OPTIONS":
        # 프리플라이트 빠른 승인
        return ("", 200)

    # 사진 4장 + 옵션
    data = request.get_json(force=True)
    photos = data.get("photos", [])
    grayscale = data.get("grayscale", False)
    frame_key = data.get("frameKey")  # 프론트에서 선택한 프레임 키(예: frame1/frame2/...)

    if len(photos) != 4:
        return jsonify({"message": "사진 4장이 필요합니다."}), 400

    frame_path = FRAME_MAP.get(frame_key)
    if not frame_path or not os.path.exists(frame_path):
        return jsonify({"message": f"프레임 경로 없음: {frame_key} → {frame_path}"}), 400

    strip = make_4cut(photos, frame_path, grayscale)

    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(FINALS_FOLDER, filename)
    strip.save(filepath, quality=92)

    from urllib.parse import urljoin
    public_url = urljoin(request.host_url, f"finals/{filename}")
    return jsonify({"url": public_url})

# 저장된 파일 서빙
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/finals/<filename>')
def get_final(filename):
    return send_from_directory(FINALS_FOLDER, filename)

# =========================
# 메인 실행
# =========================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
