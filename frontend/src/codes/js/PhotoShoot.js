// 실제 웹캠 촬영 + Flask 백엔드 전송
//flask app.py에서 /uploads로 받아 이미지 저장 및 가공
import React, { useState, useEffect, useRef, useCallback } from 'react';
import '../css/PhotoShoot.css';

const PhotoShoot = ({ onComplete }) => {
  const [countdown, setCountdown] = useState(10);
  const [photoCount, setPhotoCount] = useState(0);
  const [isShooting, setIsShooting] = useState(false);
  const [capturedPhotoUrls, setCapturedPhotoUrls] = useState([]);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const timerIdRef = useRef(null);

  // 웹캠 설정
  useEffect(() => {
    const getCameraStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 640, height: 480 } 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("카메라 접근 오류:", err);
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
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = canvas.toDataURL('image/jpeg');
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
          setTimeout(() => setIsShooting(false), 500);
          capturePhotoAndSend();
          setPhotoCount(count => count + 1);
          return 1;//시간 조절하기

        }
        return prev - 1;
      });
    }, 1000);

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
    </div>
  );
};

export default PhotoShoot;