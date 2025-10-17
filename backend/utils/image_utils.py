# 사진 4장 합성 로직
# 각 프레임에 맞는 PNG 불러오기
# # 좌표 비율에 맞춰 4장 이미지를 붙이기
# 흑백 변환(grayscale)
# 완성된 이미지 저장 후 경로 반환

import os
from PIL import Image, ImageOps
from utils.file_utils import FRAME_DIR, FINAL_DIR, UPLOAD_DIR

# 프레임별 4컷 좌표 비율 정의
FRAME_POSITIONS = {
    "BlackRoundFrame": [
        {"x": 23.71 / 592.67, "y": 29.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        {"x": 23.71 / 592.67, "y": 393.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        {"x": 23.71 / 592.67, "y": 756.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        {"x": 23.71 / 592.67, "y": 1120.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
    ],
    "BlackTextFrame": [
        {"x": 23.71 / 592.67, "y": 29.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        {"x": 23.71 / 592.67, "y": 393.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        {"x": 23.71 / 592.67, "y": 756.63 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
        {"x": 23.71 / 592.67, "y": 1120.13 / 1778, "w": 545.24 / 592.67, "h": 344.73 / 1778},
    ],
    # 나머지 프레임 동일 좌표 등록
    "OceanRoundFrame": None,
    "OceanTextFrame": None,
    "PartyRoundFrame": None,
    "PartyTextFrame": None,
    "ShinguFrame": None,
    "StarRoundFrame": None,
    "StarTextFrame": None,
    "WhiteRoundFrame": None,
    "WhiteTextFrame": None,
    "ZebraRoundFrame": None,
    "ZebraTextFrame": None,
}

for key, val in list(FRAME_POSITIONS.items()):
    if val is None:
        FRAME_POSITIONS[key] = FRAME_POSITIONS["BlackRoundFrame"]

def combine_photos(photos, frame_key, grayscale, output_filename):
    """
    4컷 프레임 합성 함수

    Args:
        photos (list): 업로드된 사진 경로 리스트 (ex. ["/uploads/1018_img1_01.jpg", ...])
        frame_key (str): 프레임 이름 (ex. "ZebraRoundFrame")
        grayscale (bool): 흑백 변환 여부
        output_filename (str): 완성 이미지 파일 이름 (ex. "1018_img1.png")

    Returns:
        str: 합성 완료된 최종 이미지의 로컬 경로
    """
    # 프레임 경로
    frame_path = os.path.join(FRAME_DIR, f"{frame_key}.png")
    if not os.path.exists(frame_path):
        raise FileNotFoundError(f"프레임 파일을 찾을 수 없습니다: {frame_path}")

    frame = Image.open(frame_path).convert("RGBA")
    frame_w, frame_h = frame.size

    # 프레임 좌표
    base_positions = FRAME_POSITIONS.get(frame_key)
    if base_positions is None:
        raise ValueError(f"등록되지 않은 프레임 키입니다: {frame_key}")

    # 실제 픽셀 단위로 변환
    positions = [
        {
            "x": int(p["x"] * frame_w),
            "y": int(p["y"] * frame_h),
            "width": int(p["w"] * frame_w),
            "height": int(p["h"] * frame_h),
        }
        for p in base_positions
    ]

    # 4장 이미지 합성
    for i, photo_url in enumerate(photos[:4]):
        pos = positions[i]
        filename = os.path.basename(photo_url)
        photo_path = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(photo_path):
            print(f"⚠️ 사진 파일이 존재하지 않습니다: {photo_path}")
            continue

        img = Image.open(photo_path).convert("RGBA").resize(
            (pos["width"], pos["height"])
        )

        if grayscale:
            img = ImageOps.grayscale(img).convert("RGBA")

        frame.paste(img, (pos["x"], pos["y"]), img)

    # ✅ 최종 파일 저장
    output_path = os.path.join(FINAL_DIR, output_filename)
    frame.save(output_path)
    print(f"✅ 합성 완료 → {output_path}")
    
    return output_path
