// 실제 웹캠 촬영 + Flask 백엔드 전송
// flask app.py에서 /uploads로 받아 이미지 저장 및 가공
import React, { useState, useEffect, useRef, useCallback } from "react";
import "../css/PhotoShoot.css";
import BASE_URL from "../../config";

// Flask 서버 주소 (EC2 IP)
const API_BASE_URL = BASE_URL;

const PhotoShoot = ({ onComplete }) => {
  const [countdown, setCountdown] = useState(10); // 카운트다운 (초)
  const [photoCount, setPhotoCount] = useState(0);
  const [isShooting, setIsShooting] = useState(false);
  const [capturedPhotoUrls, setCapturedPhotoUrls] = useState([]);
  const [cameraError, setCameraError] = useState(false); // 카메라 오류 상태

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const timerIdRef = useRef(null);

  // 종횡비 (16:10)
  const SLOT_AR = 16 / 10;

  // === 📸 카메라 초기화 ===
  useEffect(() => {
    const getCameraStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            aspectRatio: SLOT_AR,
            width: { ideal: 1280 },
            height: { ideal: 800 },
          },
        });
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (err) {
        console.error("카메라 접근 오류:", err);
        setCameraError(true);
        alert("카메라를 사용할 수 없습니다. 브라우저 설정을 확인해주세요.");
      }
    };
    getCameraStream();

    // cleanup
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // === 📤 사진 캡처 + Flask 전송 ===
  const capturePhotoAndSend = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;

    // 출력 크기 (16:10)
    const OUT_W = 1600;
    const OUT_H = 1000;
    canvas.width = OUT_W;
    canvas.height = OUT_H;

    const ctx = canvas.getContext("2d");
    const vw = video.videoWidth;
    const vh = video.videoHeight;
    const videoAR = vw / vh;

    let sx, sy, sw, sh;
    if (videoAR > SLOT_AR) {
      // 가로가 더 넓음
      sh = vh;
      sw = Math.round(vh * SLOT_AR);
      sx = Math.round((vw - sw) / 2);
      sy = 0;
    } else {
      // 세로가 더 김
      sw = vw;
      sh = Math.round(vw / SLOT_AR);
      sx = 0;
      sy = Math.round((vh - sh) / 2);
    }

    // 1. x축을 캔버스 너비만큼 오른쪽으로 이동 (캔버스의 0점이 오른쪽 끝으로 이동)
    ctx.translate(OUT_W, 0);
    // 2. x축 방향으로 -1 스케일 (좌우 반전)
    ctx.scale(-1, 1);

    // 영상에서 캔버스로 크롭
    ctx.drawImage(video, sx, sy, sw, sh, 0, 0, OUT_W, OUT_H);
    const imageData = canvas.toDataURL("image/jpeg", 0.92);

    try {
      console.log(`${photoCount + 1}번째 사진을 백엔드로 전송합니다.`);

      const response = await fetch(`${API_BASE_URL}/capture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image: imageData,
          group: "img1",
          index: photoCount + 1,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      if (result.error) throw new Error(result.error);

      console.log("✅ 백엔드 응답 완료:", result.imageUrl);
      setCapturedPhotoUrls((prev) => [...prev, result.imageUrl]);
    } catch (error) {
      console.error("❌ 백엔드 통신 오류:", error);
    }
  }, [photoCount]);

  // === ⏱️ 타이머 로직 ===
  useEffect(() => {
    if (photoCount >= 8) {
      if (timerIdRef.current) clearInterval(timerIdRef.current);
      return;
    }

    timerIdRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timerIdRef.current);
          setIsShooting(true);
          setTimeout(() => setIsShooting(false), 500);
          capturePhotoAndSend();
          setPhotoCount((count) => count + 1);
          return 10;
        }
        return prev - 1;
      });
    }, 1000); // 1초 간격

    return () => {
      if (timerIdRef.current) clearInterval(timerIdRef.current);
    };
  }, [photoCount, capturePhotoAndSend]);

  // === 📁 촬영 완료 후 다음 페이지로 ===
  useEffect(() => {
    if (capturedPhotoUrls.length === 8) {
      console.log("📸 8장 촬영 완료! 다음 페이지로 이동합니다.");
      console.log("전달할 사진 URL:", capturedPhotoUrls);
      setTimeout(() => {
        if (onComplete) onComplete(capturedPhotoUrls);
      }, 2000);
    }
  }, [capturedPhotoUrls, onComplete]);

  const getCountdownClass = () => {
    if (countdown <= 3 && countdown > 0) return "countdown-number red";
    return "countdown-number";
  };

  const isComplete = capturedPhotoUrls.length >= 8;

  // === ⚙️ 임시 "다음으로 이동" 버튼 ===
  const handleSkipToNext = () => {
    const dummyUrls = Array(8)
      .fill()
      .map((_, index) => `dummy-photo-${index + 1}.jpg`);
    if (onComplete) onComplete(dummyUrls);
  };

  if (isComplete) {
    return (
      <div className="photo-shoot-container">
        <div className="complete-message">촬영이 완료되었습니다!</div>
      </div>
    );
  }

  return (
    <div className="photo-shoot-container">
      <div className="camera-screen">
        <video ref={videoRef} autoPlay playsInline muted />
      </div>

      <canvas ref={canvasRef} style={{ display: "none" }} />

      <div className="photo-count">
        <div className="count-label">촬영 횟수</div>
        <div className="count-number">{photoCount}/8</div>
      </div>

      <div className="divider"></div>

      <div className="time-remaining">
        <div className="time-label">남은 시간</div>
        <div className={getCountdownClass()}>
          {countdown > 0 ? countdown : "찰칵!"}
        </div>
      </div>

      {isShooting && (
        <div className="shooting-overlay">
          <div className="shooting-effect">📸</div>
        </div>
      )}

      {/* 개발용: 임시 다음 페이지 버튼 */}
      <div className="emergency-controls">
        <button
          className="skip-button"
          onClick={handleSkipToNext}
          style={{
            position: "absolute",
            bottom: "20px",
            right: "20px",
            padding: "10px 20px",
            backgroundColor: "#ff4444",
            color: "white",
            border: "none",
            borderRadius: "5px",
            fontSize: "16px",
            cursor: "pointer",
            zIndex: 1000,
          }}
        >
          다음 페이지로 이동 (개발용)
        </button>
      </div>
    </div>
  );
};

export default PhotoShoot;
