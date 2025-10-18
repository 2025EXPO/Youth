# Flask 진입점
# routes/ 폴더에 있는 각 기능별 /capture, /final, /print, /health 라우트를 Flask에 연결

import os

from flask import Flask, send_from_directory 
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

# uploads 폴더 경로
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# final 폴더 경로
FINAL_DIR = os.path.join(os.getcwd(), "final")

@app.route("/final/<path:filename>")
def serve_final(filename):
    return send_from_directory(FINAL_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
