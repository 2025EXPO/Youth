// 찍을 사진 개수 선택
import React, { useState, useEffect } from 'react';
import '../css/NumSelect.css';
import NextArrow from "../../img/NextArrow.png";
import BackArrow from "../../img/BackArrow.png";
import EllipseCircle from "../../img/EllipseCircle.png";

const BackButton = ({ onClick }) => {
  return (
    <div className="back-button-container" onClick={onClick}>
      <div className="back-button">
        <div className="back-button-border"></div>
        <div className="back-text">BACK</div>
        <div className="numselect-back-arrow">
          <img alt="back arrow" src={BackArrow} />
        </div>
      </div>
    </div>
  );
};

const NextButton = ({ onClick }) => {
  return (
    <div className="next-button-container" onClick={onClick}>
      <div className="next-button">
        <div className="next-button-border"></div>
        <div className="next-text">NEXT</div>
        <div className="numselect-next-arrow">
          <img alt="next arrow" src={NextArrow} />
        </div>
      </div>
    </div>
  );
};

// App.js로부터 onBack과 onNext를 props로 받습니다.
const NumSelect = ({ onBack, onNext, initialCount = 1 }) => {
  const [photoCount, setPhotoCount] = useState(initialCount);

  useEffect(() => {
    setPhotoCount(initialCount);
  }, [initialCount]);

  const handleDecrease = () => {
    if (photoCount > 1) {
      setPhotoCount(photoCount - 1);
    }
  };

  const handleIncrease = () => {
    if (photoCount < 10) { 
      setPhotoCount(photoCount + 1);
    }
  };

  const handleBack = () => {
    if (onBack) {
      onBack();
    }
  };

  const handleNext = () => {
    // ====================== 디버깅 로그 1 ======================
    // NEXT 버튼이 실제로 클릭되었는지 확인합니다.
    console.log("NextButton 클릭됨! handleNext 함수 실행.");
    
    // ====================== 디버깅 로그 2 ======================
    // App.js로부터 onNext prop을 제대로 받았는지 확인합니다.
    // 여기서 함수가 보이면 정상, undefined가 보이면 App.js의 문제입니다.
    console.log("전달받은 onNext prop:", onNext);
    // ========================================================

    if (onNext) {
      onNext(photoCount);
    }
  };

  return (
    <div className="num-select-container">
      <div className="title-text">
        사진 수량을 선택해 주세요.
      </div>
      <div className="counter-section">
        <div 
          className={`minus-button ${photoCount <= 1 ? 'disabled' : ''}`}
          onClick={handleDecrease}
        >
          <img alt="minus circle" src={EllipseCircle} />
          <div className="minus-line"></div>
        </div>
        <div className="count-display">
          {photoCount}
        </div>
        <div 
          className={`plus-button ${photoCount >= 10 ? 'disabled' : ''}`}
          onClick={handleIncrease}
        >
          <img alt="plus circle" src={EllipseCircle} />
          <div className="plus-line-horizontal"></div>
          <div className="plus-line-vertical"></div>
        </div>
      </div>
      <div className="bottom-buttons">
        <BackButton onClick={handleBack} />
        <NextButton onClick={handleNext} />
      </div>
    </div>
  );
};

export default NumSelect;