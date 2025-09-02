import React, { useState, useEffect } from 'react';
import '../css/MainNoon.css';
import youthLogo from '../../img/Union.png';
import imgCloudLower from '../../img/CloudLower.png';
import imgCloudUpper from '../../img/CloudUpper.png';

const MainNoon = ({ onStartClick }) => {
  const [fadeClass, setFadeClass] = useState('fade-in');
  const [touchFeedback, setTouchFeedback] = useState(false);

  // Touch to start 페이드 애니메이션 (3초마다 반복)
  useEffect(() => {
    const interval = setInterval(() => {
      setFadeClass('fade-out');
      setTimeout(() => {
        setFadeClass('fade-in');
      }, 1000);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // 터치 피드백 핸들러
  const handleTouch = () => {
    setTouchFeedback(true);
    setTimeout(() => {
      setTouchFeedback(false);
    }, 200);
    
    // App.js의 onStartClick을 호출하여 NumSelect 화면으로 전환
    if (onStartClick) {
      onStartClick();
    }
  };

  return (
    <div 
      className={`main-noon ${touchFeedback ? 'touch-active' : ''}`}
      onClick={handleTouch}
      onTouchStart={handleTouch}
    >
      {/* 구름 */}
      <div className="figma-cloud figma-cloud-lower">
        <img src={imgCloudLower} alt="Lower Cloud" className="figma-cloud-img" />
      </div>
      <div className="figma-cloud figma-cloud-upper">
        <img src={imgCloudUpper} alt="Upper Cloud" className="figma-cloud-img" />
      </div>
      
      {/* 로고 */}
      <div className="logo-container">
        <img src={youthLogo} alt="Youth" className="youth-logo" />
      </div>
      
      {/* Touch to start*/}
      <div className={`touch-text ${fadeClass}`}>
        Touch to start!
      </div>
    </div>
  );
};

export default MainNoon;