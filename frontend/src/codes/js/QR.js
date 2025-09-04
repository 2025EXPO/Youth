// 최종 QR코드 화면 (s3버킷을이용해 qr생성)
import React from 'react';
import '../css/QR.css';
import QRCode from "../../img/QR_Sample.svg";

const QR = ({ onComplete }) => {
  const [countdown, setCountdown] = React.useState(30);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // 카운트다운이 끝나면 MainNoon으로 이동
          if (onComplete) {
            onComplete();
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className="qr-container">
      {/* 제목 */}
      <div className="qr-title">
        QR코드로 사진을 다운받으세요!
      </div>

      {/* 메인 콘텐츠 */}
      <div className="qr-main-content">
        {/* QR 코드 섹션 */}
        <div className="qr-code-section">
          <div className="qr-code-container">
            <img src={QRCode} alt="QR Code" className="qr-code-image" />
          </div>
          <div className="qr-instruction">
            <p>스마트폰으로 QR코드를 스캔하여</p>
            <p>사진을 다운받으세요</p>
            <div className="qr-countdown">
              <span className="qr-countdown-number">{countdown}</span>
            </div>
          </div>
        </div>


      </div>


    </div>
  );
};

export default QR;
