// 시작 시 카운트다운
import React, { useState, useEffect } from 'react';
import '../css/Start.css';

const Start = ({ onComplete }) => {
  const [countdown, setCountdown] = useState(5);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    // [핵심 1] timer 변수를 useEffect 바깥에서도 접근할 수 있도록 선언합니다.
    let timer;

    // isComplete가 true가 되면 더 이상 타이머를 진행하지 않도록 막습니다.
    if (!isComplete) {
      timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            // [핵심 2] 타이머를 즉시 멈춥니다.
            clearInterval(timer); 
            
            setIsComplete(true); // UI를 'now!'로 변경
            
            // 1초 후에 다음 페이지로 전환합니다.
            setTimeout(() => {
              if (onComplete) onComplete();
            }, 1000);
            
            return 0; // 카운트다운을 0으로 설정
          }
          return prev - 1; // 1씩 감소
        });
      }, 1000);
    }

    // [핵심 3] 컴포넌트가 사라질 때(unmount)나 재렌더링될 때 타이머를 정리합니다.
    return () => {
      if (timer) {
        clearInterval(timer);
      }
    };
    // onComplete와 isComplete가 바뀔 때마다 이 useEffect를 재실행합니다.
  }, [onComplete, isComplete]);

  const getText = () => {
    if (isComplete) return 'now!';
    return `in ${countdown}`;
  };

  const getClass = () => {
    if (isComplete) return 'countdown-text complete';
    return 'countdown-text animated';
  };

  return (
    <div className="start-container">
      <div className="start-text">START!</div>
      <div className={getClass()}>
        {getText()}
      </div>
    </div>
  );
};

export default Start;