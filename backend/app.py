# 필요한 라이브러리들을 가져옵니다.
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import base64
import os
import uuid 
from PIL import Image, ImageOps 

# Flask 앱을 생성합니다.
app = Flask(__name__)
CORS(app)

# 현재 파일(app.py)이 있는 폴더의 절대 경로를 가져옵니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 사진을 저장할 폴더를 절대 경로로 지정합니다.
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return "백엔드 서버가 작동 중입니다. /test 로 이동하여 테스트하세요."

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

if __name__ == '__main__':
    app.run(debug=True)