import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# 설정 파일
from config import Config

# 라우트 불러오기
from routes.capture_route import capture_bp
from routes.final_route import final_bp
from routes.print_route import print_bp
from routes.health_route import health_bp

# Flask 앱 생성
app = Flask(__name__)

#전역 설정 적용
app.config.from_object(Config)

# CORS 허용
CORS(app)

# 블루프린트 등록
app.register_blueprint(capture_bp)
app.register_blueprint(final_bp)
app.register_blueprint(print_bp)
app.register_blueprint(health_bp)

# uploads 폴더
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_DIR"], filename)

# final 폴더 정적 서빙
@app.route("/final/<path:filename>")
def serve_final(filename):
    return send_from_directory(app.config["FINAL_DIR"], filename)

# print 폴더 정적 서빙
@app.route("/print/<path:filename>")
def serve_print(filename):
    return send_from_directory(app.config["PRINT_DIR"], filename)

if __name__ == "__main__":
    print("🚀 Flask 서버 실행 중")
    print(f"🌐 BASE_URL: {Config.BASE_URL}")
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])