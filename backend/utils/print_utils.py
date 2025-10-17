# PDF 생성 및 프린터
# 인쇄용 PDF 생성 (reportlab 사용)
# 실제 프린터로 자동 출력 명령 전송 (lp 등)

import os
import uuid
import subprocess
from PIL import Image
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas

DPI = 300
PRINT_DIR = "print"

# 4x6 인치 = 10.16 x 15.24 cm (세로형)
TARGET_WIDTH_CM = 10.16   # 4 inch
TARGET_HEIGHT_CM = 15.24  # 6 inch


def make_print_pdf(image_path: str) -> str:
    """두 장 이미지를 4x6 인치(세로 인화지)에 맞게 PDF로 변환"""
    if not os.path.exists(PRINT_DIR):
        os.makedirs(PRINT_DIR, exist_ok=True)

    img = Image.open(image_path)
    w, h = img.size

    # ✅ 두 장 나란히 합치기 (가로로)
    combined = Image.new("RGB", (w * 2, h), (255, 255, 255))
    combined.paste(img, (0, 0))
    combined.paste(img, (w, 0))

    # ✅ 4x6 인치 (300 DPI = 1200x1800px) 기준 리사이즈 (비율 유지)
    target_width_px = int(TARGET_WIDTH_CM / 2.54 * DPI)   # ≈ 1200px
    target_height_px = int(TARGET_HEIGHT_CM / 2.54 * DPI) # ≈ 1800px

    # 이미지 비율 계산
    img_ratio = combined.width / combined.height
    target_ratio = target_width_px / target_height_px

    if img_ratio > target_ratio:
        # 이미지가 더 가로로 긴 경우 → 폭 기준 축소
        new_width = target_width_px
        new_height = int(target_width_px / img_ratio)
    else:
        # 세로가 더 긴 경우 → 높이 기준 축소
        new_height = target_height_px
        new_width = int(target_height_px * img_ratio)

    combined = combined.resize((new_width, new_height), Image.LANCZOS)
    print(f"📏 리사이즈됨: {new_width}×{new_height}px (4x6 인치 비율 맞춤)")

    # ✅ 흰 여백(캔버스) 추가해서 정확히 4x6 크기로 맞추기
    result = Image.new("RGB", (target_width_px, target_height_px), (255, 255, 255))
    offset_x = (target_width_px - new_width) // 2
    offset_y = (target_height_px - new_height) // 2
    result.paste(combined, (offset_x, offset_y))
    print(f"🖼️ 여백 추가 후 최종 크기: {result.size}")

    # ✅ 임시 이미지 저장 (PDF 생성용)
    temp_img = os.path.join(PRINT_DIR, f"temp_{uuid.uuid4()}.jpg")
    result.save(temp_img, quality=95, dpi=(DPI, DPI))

    # ✅ PDF 페이지 크기(mm)
    pdf_width_mm = TARGET_WIDTH_CM * 10  # cm → mm
    pdf_height_mm = TARGET_HEIGHT_CM * 10

    output_pdf = os.path.join(PRINT_DIR, f"print_{uuid.uuid4()}.pdf")
    c = canvas.Canvas(output_pdf, pagesize=(pdf_width_mm * mm, pdf_height_mm * mm))
    c.drawImage(temp_img, 0, 0, pdf_width_mm * mm, pdf_height_mm * mm)
    c.save()

    os.remove(temp_img)
    print(f"🖨️ PDF 생성 완료: {output_pdf}")
    return output_pdf


def print_pdf(file_path: str):
    """Microsoft Edge로 PDF 인쇄"""
    try:
        edge_candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        edge_path = next((p for p in edge_candidates if os.path.exists(p)), None)
        if not edge_path:
            raise FileNotFoundError("Microsoft Edge 실행 파일을 찾을 수 없습니다.")

        # ✅ Edge의 /p 옵션 → 백그라운드 인쇄
        subprocess.run([edge_path, "/p", os.path.abspath(file_path)], check=True)
        print("✅ Microsoft Edge로 인쇄 명령 전송 완료")

    except Exception as e:
        print("⚠️ Edge 인쇄 명령 실패:", e)
