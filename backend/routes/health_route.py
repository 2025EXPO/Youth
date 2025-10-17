# 서버 상태 확인용
# /health 요청 시 {"status": "ok"} 반환
# EC2, Flask 등 서버 동작 확인용

from flask import Blueprint, jsonify
health_bp = Blueprint("health", __name__)

@health_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
