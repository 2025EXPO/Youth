// 촬영한 사진 중 원하는 4장 선택

import React, { useState } from "react";
import "../css/PhotoSelect.css";
import NextArrow from "../../img/NextArrow.png"; // NumSelect에서 사용하던 이미지 재활용
import BackArrow from "../../img/BackArrow.png"; // NumSelect에서 사용하던 이미지 재활용
import Frame from "../../img/frames/WhiteRound.png";

import { getImageUrl } from "../../utils/getImageUrl";

// App.js로부터 photos, onComplete, onBack 함수를 props로 받습니다.
function PhotoSelect({ photos, onComplete, onBack }) {
    // 사용자가 선택한 사진들의 URL을 순서대로 저장하는 배열
    const [selectedPhotos, setSelectedPhotos] = useState([]);

    // 사진 클릭 이벤트 핸들러 - 선택/해제 토글 기능
    const togglePhotoSelection = (photoUrl) => {
        setSelectedPhotos((prevSelected) => {
            // 이미 선택된 사진인지 확인
            if (prevSelected.includes(photoUrl)) {
                // 이미 선택되었다면, 선택 목록에서 제거 (선택 해제)
                console.log("사진 선택 해제:", photoUrl);
                return prevSelected.filter((url) => url !== photoUrl);
            } else {
                // 아직 4장이 안 찼다면, 선택 목록에 추가
                if (prevSelected.length < 4) {
                    console.log("사진 선택:", photoUrl);
                    return [...prevSelected, photoUrl];
                } else {
                    // 4장이 꽉 찼을 때 알림
                    console.log("최대 4장까지만 선택할 수 있습니다.");
                }
            }
            // 4장이 꽉 찼고, 선택되지 않은 사진을 클릭했다면, 변경 없음
            return prevSelected;
        });
    };

    // NEXT 버튼 클릭 이벤트 핸들러
    const handleNext = () => {
        // 4장을 모두 선택했을 때만 다음 단계로 진행
        if (selectedPhotos.length === 4) {
            onComplete(selectedPhotos);
        }
    };

    return (
        // CSS 파일의 클래스 이름에 맞춰 JSX 구조를 완전히 새로 구성했습니다.
        <div className="photoselect-container">
            <h1 className="title">사진을 선택해 주세요:)</h1>

            <div className="main-content">
                {/* 왼쪽 필름 프레임 영역 */}
                <div className="film-frame">
                    <div className="photoselect-frame-container">
                        {/* 이 부분은 프레임 배경 이미지가 필요하다면 추가하세요 */}
                        <img
                            src={Frame}
                            alt="Film Frame"
                            className="photoselect-frame-image"
                        />
                        <div className="photoselect-frame-slots">
                            <div className="photoselect-frame-row">
                                {[0, 1, 2, 3].map((index) => (
                                    <div
                                        className="photoselect-frame-slot"
                                        key={index}
                                    >
                                        {selectedPhotos[index] ? (
                                            <div
                                                className="selected-photo clickable"
                                                onClick={() =>
                                                    togglePhotoSelection(
                                                        selectedPhotos[index]
                                                    )
                                                }
                                                title="클릭하여 선택 해제"
                                            >
                                                <img
                                                    src={getImageUrl(
                                                        selectedPhotos[index]
                                                    )}
                                                    alt={`선택된 사진 ${
                                                        index + 1
                                                    }`}
                                                />
                                            </div>
                                        ) : (
                                            <div className="empty-slot">
                                                <span className="photoselect-photo-placeholder">{`사진 ${
                                                    index + 1
                                                }`}</span>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 오른쪽 사진 그리드 영역 */}
                <div className="photoselect-photo-grid">
                    {photos.map((photoUrl, index) => {
                        const isSelected = selectedPhotos.includes(photoUrl);
                        const selectionIndex = selectedPhotos.indexOf(photoUrl);

                        return (
                            <div
                                key={index}
                                className={`photoselect-photo-item ${
                                    isSelected ? "selected" : ""
                                }`}
                                onClick={() => togglePhotoSelection(photoUrl)}
                            >
                                <img
                                    src={getImageUrl(photoUrl)}
                                    alt={`촬영된 사진 ${index + 1}`}
                                />

                                {isSelected && (
                                    <div className="selection-indicator">
                                        {selectionIndex + 1}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* 하단 버튼 및 상태 표시줄 */}
            <div className="photoselect-back-button-container" onClick={onBack}>
                <div className="photoselect-back-button">
                    <div className="photoselect-back-button-border"></div>
                    <div className="photoselect-back-arrow">
                        <img src={BackArrow} alt="Back" />
                    </div>
                    <div className="photoselect-back-text">BACK</div>
                </div>
            </div>

            <div className="selection-status">
                {selectedPhotos.length} / 4 사진 선택됨
            </div>

            <div
                className={`next-button-container ${
                    selectedPhotos.length !== 4 ? "disabled" : ""
                }`}
                onClick={handleNext}
            >
                <div
                    className={`next-button ${
                        selectedPhotos.length !== 4 ? "disabled" : ""
                    }`}
                >
                    <div className="next-button-border"></div>
                    <div className="next-text">NEXT</div>
                    <div className="photoselect-next-arrow">
                        <img src={NextArrow} alt="Next" />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PhotoSelect;
