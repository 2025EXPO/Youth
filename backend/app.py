# 필요한 라이브러리들을 가져옵니다.
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import base64
import os
import uuid
import io,requests
from PIL import Image, ImageOps 

# Flask 앱을 생성합니다.
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

# 현재 파일(app.py)이 있는 폴더의 절대 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 사진을 저장할 폴더를 절대 경로로 지정합니다.
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 프레임+ 선택4장의 최종네컷을 저장할 경로
FINALS_FOLDER = os.path.join(UPLOAD_FOLDER, 'finals')
os.makedirs(FINALS_FOLDER, exist_ok=True)

# 프레임 PNG 매핑
# 프레임 PNG 매핑
FRAME_MAP = {
    # Round 타입
    "frame1": os.path.join(BASE_DIR, "templates", "frames", "WhiteRound.png"),
    "frame2": os.path.join(BASE_DIR, "templates", "frames", "BlackRound.png"),
    "frame3": os.path.join(BASE_DIR, "templates", "frames", "PartyRound.png"),
    "frame4": os.path.join(BASE_DIR, "templates", "frames", "ZebraRound.png"),
    "frame5": os.path.join(BASE_DIR, "templates", "frames", "Shingu.png"),

    # Text 타입 (필요한 경우)
    "frame6": os.path.join(BASE_DIR, "templates", "frames", "WhiteText.png"),
    "frame7": os.path.join(BASE_DIR, "templates", "frames", "BlackText.png"),
    "frame8": os.path.join(BASE_DIR, "templates", "frames", "PartyText.png"),
    "frame9": os.path.join(BASE_DIR, "templates", "frames", "ZebraText.png"),
    "frame10": os.path.join(BASE_DIR, "templates", "frames", "Shingu.png"),  # 텍스트 버전 없으면 같은 거 사용

    # Special 타입 (필요한 경우)
    "special1": os.path.join(BASE_DIR, "templates", "frames", "StarRound.png"),
    "special2": os.path.join(BASE_DIR, "templates", "frames", "OceanRound.png"),
    "special3": os.path.join(BASE_DIR, "templates", "frames", "ShinguFunny.png"),
}

# 0905 수정 유틸 함수===================================================================================================
# URL 에서 바로 image.open() 불가해서 요청-메모리 올리기-PIL변환
def _open_url(url):
    r = requests.get(url, timeout=10) # url로 HTTP 요청 보내서 이미지 가져옴
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB") # rgb로 변환, 메모리에 올림

# 1열 4컷 (2*6/ 600x1800) 생성
def make_4cut(photo_urls, frame_path=None, grayscale=False):
    if not frame_path or not os.path.exists(frame_path):
        raise ValueError("Frame not found")

    # 프레임/캔버스
    frame_rgba = Image.open(frame_path).convert("RGBA")
    W, H = frame_rgba.size
    canvas = Image.new("RGBA", (W, H), "white")

    # 사진 불러오기
    imgs = [_open_url(u) for u in photo_urls]
    if grayscale:
        imgs = [ImageOps.grayscale(im).convert("RGB") for im in imgs]

    # === 슬롯(녹색 네모) 레이아웃 ===
    positions = [
        (23,29),
        (23,393),
        (23,756),
        (23,1121),
    ]

    # 슬롯의 '보이는 영역' 비율을 16:10으로 강제
    SLOT_AR = 16 / 10

    # Pillow 10 대응: 리샘플러
    try:
        RESAMPLE = Image.Resampling.LANCZOS
    except AttributeError:
        RESAMPLE = Image.LANCZOS

    # 각 슬롯에 맞춰 'object-fit: cover' 처럼 중앙 크롭 + 리사이즈
    for im, (slot_x, slot_y) in zip(imgs, positions):
        # 우선 슬롯 크기(cell_w, cell_h) 안에서 16:10을 최대한 크게 맞춤
        # 1) 가로를 기준으로 맞춰본다
        target_w = cell_w
        target_h = int(round(target_w / SLOT_AR))
        # 2) 세로가 슬롯을 넘치면 세로 기준으로 다시 계산
        if target_h > cell_h:
            target_h = cell_h
            target_w = int(round(target_h * SLOT_AR))

        # 중앙 크롭 + 리사이즈
        fitted = ImageOps.fit(im, (target_w, target_h), method=RESAMPLE, centering=(0.5, 0.5))
        fitted = fitted.convert("RGBA")

        # 슬롯 안에서 중앙 정렬(슬롯이 더 클 수 있으니까 여백 보정)
        paste_x = slot_x + (cell_w - target_w) // 2
        paste_y = slot_y + (cell_h - target_h) // 2

        canvas.paste(fitted, (paste_x, paste_y), fitted)

    # 프레임을 맨 위에 덮기 (프레임의 투명영역으로 사진이 보임)
    combined = Image.alpha_composite(canvas, frame_rgba)
    return combined.convert("RGB")


# 프린트용 네컷 2개를 좌우로 배치해서 합치기
def make_print(strip: Image.Image):
    canvas = Image.new("RGB", (1200, 1800), "white")
    canvas.paste(strip, (0, 0))
    canvas.paste(strip, (600, 0))
    return canvas

# =================================================================================================

# 라우트 정의들
@app.route('/')
def home():
    return "백엔드 서버가 작동 중입니다. /test 로 이동하여 테스트하세요."

# 0905 수정==================================================================================
@app.post("/final")
def make_final():
    # 사진 4장 프론트에서 받아서 합성 후 저장
    data = request.get_json(force=True)
    photos = data.get("photos", [])
    grayscale = data.get("grayscale", False)
    frame_key = data.get("frameKey")

    if len(photos) != 4:
        return jsonify({"message": "사진 4장이 필요합니다."}), 400

    # 1. 2*6/ 600x1800 1열 4컷 만들기
    print(">>> 요청 frame_key:", frame_key)
    frame_path = FRAME_MAP.get(frame_key)
    print(">>> frame_path:", frame_path)
    if not frame_path or not os.path.exists(frame_path):
        return jsonify({"message": f"프레임 경로 없음: {frame_key} → {frame_path}"}), 400

    strip = make_4cut(photos, frame_path, grayscale)

    # 2. 저장하기
    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(FINALS_FOLDER, filename)
    strip.save(filepath, quality=92)

    # 3) QR 생성 URL 리턴
    from urllib.parse import urljoin
    public_url = urljoin(request.host_url, f"finals/{filename}")
    return jsonify({"url": public_url})
# ==================================================================================

@app.route('/test')
def test_page():
    return render_template('test_capture.html')

@app.route('/capture', methods=['POST'])
def capture():
    if not request.is_json:
        return jsonify({"message": "요청 형식이 JSON이 아닙니다."}), 400

    data = request.get_json()
    if 'image' not in data:
        return jsonify({"message": "'image' 키가 요청에 없습니다."}), 400
        
    image_data = data['image']

    # 여기부터 try...except 블록이 시작됩니다.
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

        image_url = f"http://127.0.0.1:5000/images/{decorated_filename}"

        return jsonify({
            'message': '사진 처리 및 저장이 완료되었습니다.', 
            'imageUrl': image_url
        }), 200

    # try 블록에서 오류가 발생하면 여기가 실행됩니다.
    except Exception as e:
        print(f"!!! 서버 내부 오류 발생: {e}")
        return jsonify({'message': '사진 처리 중 서버 내부에서 오류가 발생했습니다.', 'error': str(e)}), 500

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/finals/<filename>')
def get_final(filename):
    return send_from_directory(FINALS_FOLDER, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)