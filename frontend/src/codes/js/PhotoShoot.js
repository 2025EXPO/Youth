// 실제 웹캠 촬영 + Flask 백엔드 전송
// flask app.py에서 /uploads로 받아 이미지 저장 및 가공
import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../css/PhotoShoot.css';

const PhotoShoot = ({ onComplete }) => {
  const [countdown, setCountdown] = useState(10); //카운트다운 숫자 (10초로 설정)
  const [photoCount, setPhotoCount] = useState(0);
  const [isShooting, setIsShooting] = useState(false);
  const [capturedPhotoUrls, setCapturedPhotoUrls] = useState([]);
  const [cameraError, setCameraError] = useState(false); // 카메라 오류 상태
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const timerIdRef = useRef(null);
  // 16:10 = 1.6
  const SLOT_AR = 16 / 10;

  // 웹캠 설정
  useEffect(() => {
    const getCameraStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { aspectRatio: SLOT_AR, width: { ideal: 1280 }, height: { ideal: 800 }, }
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("카메라 접근 오류:", err);
        setCameraError(true);
        alert("카메라를 사용할 수 없습니다. 브라우저 설정을 확인해주세요.");
      }
    };
    getCameraStream();
    
    // 컴포넌트가 사라질 때 웹캠 스트림 정리
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []); // 최초 1회만 실행

  // 사진 촬영 및 백엔드 전송 함수 (useCallback으로 불필요한 재생성 방지)
  const capturePhotoAndSend = useCallback(async () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;

// 최종 내보낼 크기(16:10). 슬롯이랑 맞추기
      const OUT_W = 1600;   // 원하면 1280, 960 등으로 줄여도 됨
      const OUT_H = 1000;   // 16:10 유지
      canvas.width  = OUT_W;
      canvas.height = OUT_H;

      const ctx = canvas.getContext('2d');

      // 소스(비디오)와 타겟(슬롯)의 종횡비 계산
      const SLOT_AR = 16 / 10;
      const vw = video.videoWidth;
      const vh = video.videoHeight;
      const videoAR = vw / vh;

      // 중앙 크롭용 소스 사각형 계산 (object-fit: cover)
      let sx, sy, sw, sh;
      if (videoAR > SLOT_AR) {
        // 비디오가 더 가로로 넓음 → 가로를 잘라냄
        sh = vh;
        sw = Math.round(vh * SLOT_AR);
        sx = Math.round((vw - sw) / 2);
        sy = 0;
      } else {
        // 비디오가 더 세로로 큼 → 세로를 잘라냄
        sw = vw;
        sh = Math.round(vw / SLOT_AR);
        sx = 0;
        sy = Math.round((vh - sh) / 2);
      }

      // 잘라서 16:10 캔버스에 정확히 채우기
      ctx.drawImage(video, sx, sy, sw, sh, 0, 0, OUT_W, OUT_H);

      const imageData = canvas.toDataURL("image/jpeg", 0.92);


      // const context = canvas.getContext('2d');
      // context.drawImage(video, 0, 0, canvas.width, canvas.height);
      //
      // const imageData = canvas.toDataURL('image/jpeg');

      try {
        console.log(`${photoCount + 1}번째 사진을 백엔드로 전송합니다.`);
        const response = await fetch('http://127.0.0.1:5000/capture', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageData }),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.message);
        console.log('백엔드 응답 완료:', result.imageUrl);
        setCapturedPhotoUrls(prevUrls => [...prevUrls, result.imageUrl]);
      } catch (error) {
        console.error("백엔드 통신 오류:", error);
      }
    }
  }, [photoCount]); // photoCount가 바뀔 때만 이 함수가 새로 만들어짐

  // 타이머 로직
  useEffect(() => {
    if (photoCount >= 8) {
      if (timerIdRef.current) clearInterval(timerIdRef.current);
      return;
    }

    timerIdRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timerIdRef.current);
          setIsShooting(true);
          setTimeout(() => setIsShooting(false), 500); // 촬영 효과 0.5초
          capturePhotoAndSend();
          setPhotoCount(count => count + 1);
          return 10; // 다음 촬영을 위해 10초로 리셋
        }
        return prev - 1;
      });
    }, 1000); // 1초마다 카운트다운

    return () => {
      if (timerIdRef.current) clearInterval(timerIdRef.current);
    };
  }, [photoCount, capturePhotoAndSend]);

  // 촬영 완료 시 페이지 전환
  useEffect(() => {
    if (capturedPhotoUrls.length === 8) {
      console.log('8회 촬영 및 URL 수신 완료! 다음 페이지로 전환합니다.');
      setTimeout(() => {
        if (onComplete) onComplete(capturedPhotoUrls);
      }, 2000);
    }
  }, [capturedPhotoUrls, onComplete]);

  const getCountdownClass = () => {
    if (countdown <= 3 && countdown > 0) return 'countdown-number red';
    return 'countdown-number';
  };

  const isComplete = capturedPhotoUrls.length >= 8;

  // 임시 다음 페이지로 넘어가는 함수
  const handleSkipToNext = () => {
    // 더미 URL 배열 생성 (8개)
    const dummyUrls = Array(8).fill().map((_, index) => `dummy-photo-${index + 1}.jpg`);
    if (onComplete) onComplete(dummyUrls);
  };

  if (isComplete) {
    return (
      <div className="photo-shoot-container">
        <div className="complete-message">
          촬영이 완료되었습니다!
        </div>
      </div>
    );
  }

  return (
    <div className="photo-shoot-container">
      <div className="camera-screen">
        <video ref={videoRef} autoPlay playsInline muted />
      </div>
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <div className="photo-count">
        <div className="count-label">촬영 횟수</div>
        <div className="count-number">{photoCount}/8</div>
      </div>
      <div className="divider"></div>
      <div className="time-remaining">
        <div className="time-label">남은 시간</div>
        <div className={getCountdownClass()}>
          {countdown > 0 ? countdown : '찰칵!'}
        </div>
      </div>
      {isShooting && (
        <div className="shooting-overlay">
          <div className="shooting-effect">📸</div>
        </div>
      )}
      
      {/* ======================================================
          [임시 기능] 개발 및 테스트용 Next 버튼
          - 목적: 빠른 페이지 전환 테스트
          - 위치: 우측 하단 고정
          - 기능: 더미 이미지 URL 생성 후 다음 페이지로 전환
          
          [삭제 방법]
          1. 이 주석 블록 전체 삭제
          2. 상단의 handleSkipToNext 함수 삭제
          ====================================================== */}
      <div className="emergency-controls">
        <button 
          className="skip-button" 
          onClick={handleSkipToNext}
          style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            padding: '10px 20px',
            backgroundColor: '#ff4444',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            fontSize: '16px',
            cursor: 'pointer',
            zIndex: 1000
          }}
        >
          다음 페이지로 이동 (개발용)
        </button>
      </div>
    </div>
  );
};

export default PhotoShoot;