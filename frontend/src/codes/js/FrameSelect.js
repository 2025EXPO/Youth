// 프레임 + 로고 + 흑백/컬러 선택
import React, { useState, useEffect } from 'react';
import '../css/FrameSelect.css';
import WhiteRoundFrame from '../../img/frames/WhiteRound.png';
import StarRoundFrame from '../../img/frames/StarRound.png';
import OceanRoundFrame from '../../img/frames/OceanRound.png';
import ShinguFunnyFrame from '../../img/frames/ShinguFunny.png';
import StarTextFrame from '../../img/frames/StarText.png';
import OceanTextFrame from '../../img/frames/OceanText.png';
import BlackRoundFrame from '../../img/frames/BlackRound.png';
import PartyRoundFrame from '../../img/frames/PartyRound.png';
import ZebraRoundFrame from '../../img/frames/ZebraRound.png';
import ShinguFrame from '../../img/frames/Shingu.png';
import WhiteTextFrame from '../../img/frames/WhiteText.png';
import BlackTextFrame from '../../img/frames/BlackText.png';
import PartyTextFrame from '../../img/frames/PartyText.png';
import ZebraTextFrame from '../../img/frames/ZebraText.png';
import NextArrow from "../../img/NextArrow.png";
import BackArrow from "../../img/BackArrow.png";
import LogoRound from "../../img/logos/LogoRound.png";
import LogoText from "../../img/logos/LogoText.png";
import Color from "../../img/logos/Color.png";
import BlackWhite from "../../img/logos/BlackWhite.png";
import FrameStar from "../../img/logos/FrameStar.png";
import FrameOcean from "../../img/logos/FrameOcean.png";
import FrameShinguFun from "../../img/logos/FrameShinguFun.png";
import FrameWhite from "../../img/logos/FrameWhite.png";
import FrameBlack from "../../img/logos/FrameBlack.png";
import FrameZebra from "../../img/logos/FrameZebra.png";
import FrameParty from "../../img/logos/FrameParty.png";
import FrameShingu from "../../img/logos/FrameShingu.png";

const FrameSelect = ({ selectedPhotos, onComplete, onBack }) => {
  const [selectedFrame, setSelectedFrame] = useState('frame1');
  const [selectedLogo, setSelectedLogo] = useState('logo1');
  const [selectedPhotoColor, setSelectedPhotoColor] = useState('color1'); // 'color1'은 컬러, 'color2'는 흑백
  const [selectedSpecialFrame, setSelectedSpecialFrame] = useState(null);
  
  const [currentFrameImage, setCurrentFrameImage] = useState(WhiteRoundFrame);
  
  useEffect(() => {
    setCurrentFrameImage(getFrameImage());
  }, [selectedLogo, selectedSpecialFrame, selectedFrame]);
  
  const getFrameImage = () => { /* 이전과 동일한 코드 */
    if (selectedSpecialFrame) { if (selectedLogo === 'logo1') { switch (selectedSpecialFrame) { case 'special1': return StarRoundFrame; case 'special2': return OceanRoundFrame; case 'special3': return ShinguFunnyFrame; default: return WhiteRoundFrame; } } else if (selectedLogo === 'logo2') { switch (selectedSpecialFrame) { case 'special1': return StarTextFrame; case 'special2': return OceanTextFrame; case 'special3': return ShinguFunnyFrame; default: return WhiteRoundFrame; } } }
    if (selectedFrame) { if (selectedLogo === 'logo1') { switch (selectedFrame) { case 'frame1': return WhiteRoundFrame; case 'frame2': return BlackRoundFrame; case 'frame3': return PartyRoundFrame; case 'frame4': return ZebraRoundFrame; case 'frame5': return ShinguFrame; default: return WhiteRoundFrame; } } else if (selectedLogo === 'logo2') { switch (selectedFrame) { case 'frame1': return WhiteTextFrame; case 'frame2': return BlackTextFrame; case 'frame3': return PartyTextFrame; case 'frame4': return ZebraTextFrame; case 'frame5': return ShinguFrame; default: return WhiteRoundFrame; } } }
    return WhiteRoundFrame;
  };

  const handleFrameSelect = (frameType, frameId) => {
    switch (frameType) {
      case 'logo': setSelectedLogo(frameId); break;
      case 'photoColor': setSelectedPhotoColor(frameId); break;
      case 'specialFrame': setSelectedSpecialFrame(frameId); setSelectedFrame(null); break;
      case 'frame': setSelectedFrame(frameId); setSelectedSpecialFrame(null); break;
      default: break;
    }
  };

  const handleBack = () => { if (onBack) onBack(); };
  // 0905 수정===================================================================
  const handleNext = async () => {
    try {
      const res = await fetch("http://192.168.200.144:5000/final", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        mode: "cors",
        body: JSON.stringify({
          photos: selectedPhotos, // 4장 선택된 거
          grayscale: selectedPhotoColor === "color2", // 흑백 옵션
          frameKey: selectedSpecialFrame || selectedFrame,
          logoKey: selectedLogo,
          specialFrameKey: selectedSpecialFrame
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "최종본 생성 실패");

      // 최종 URL을 상위(App.js)로 전달
      onComplete && onComplete({ finalUrl: data.url });
    } catch (error) {
      console.error("최종 합성 요청 오류:", error);
      alert("최종 이미지 생성에 실패했습니다.");
    }
  };
  // ========================================================================================

  return (
    <div className="frameselect-container">
      <div className="frameselect-title">프레임을 선택해 주세요!</div>
      <div className="frameselect-main-content">
        <div className="frameselect-film-frame">
          <div className="frameselect-frame-container">
            <img src={currentFrameImage} alt="Frame" className="frameselect-frame-image" />
            <div className="frameselect-frame-slots">
              <div className="frameselect-frame-row">
                <div className="frameselect-frame-slot">
                  {selectedPhotos && selectedPhotos[0] ? (<div className="frameselect-selected-photo"><img src={selectedPhotos[0]} alt="선택된 사진 1" className={selectedPhotoColor === 'color2' ? 'grayscale' : ''} /></div>) : (<div className="frameselect-empty-slot"><span>사진 1</span></div>)}
                </div>
              </div>
              <div className="frameselect-frame-row">
                <div className="frameselect-frame-slot">
                  {selectedPhotos && selectedPhotos[1] ? (<div className="frameselect-selected-photo"><img src={selectedPhotos[1]} alt="선택된 사진 2" className={selectedPhotoColor === 'color2' ? 'grayscale' : ''} /></div>) : (<div className="frameselect-empty-slot"><span>사진 2</span></div>)}
                </div>
              </div>
              <div className="frameselect-frame-row">
                <div className="frameselect-frame-slot">
                  {selectedPhotos && selectedPhotos[2] ? (<div className="frameselect-selected-photo"><img src={selectedPhotos[2]} alt="선택된 사진 3" className={selectedPhotoColor === 'color2' ? 'grayscale' : ''} /></div>) : (<div className="frameselect-empty-slot"><span>사진 3</span></div>)}
                </div>
              </div>
              <div className="frameselect-frame-row">
                <div className="frameselect-frame-slot">
                  {selectedPhotos && selectedPhotos[3] ? (<div className="frameselect-selected-photo"><img src={selectedPhotos[3]} alt="선택된 사진 4" className={selectedPhotoColor === 'color2' ? 'grayscale' : ''} /></div>) : (<div className="frameselect-empty-slot"><span>사진 4</span></div>)}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="frameselect-options">
          <div className="frameselect-option-section">
            <div className="frameselect-section-title">Logo</div>
            <div className="frameselect-option-buttons">
              <button className={`frameselect-option-button ${selectedLogo === 'logo1' ? 'selected' : ''}`} onClick={() => handleFrameSelect('logo', 'logo1')}><img src={LogoRound} alt="Logo Round"></img></button>
              <button className={`frameselect-option-button ${selectedLogo === 'logo2' ? 'selected' : ''}`} onClick={() => handleFrameSelect('logo', 'logo2')}><img src={LogoText} alt="Logo Text"></img></button>
            </div>
          </div>
          <div className="frameselect-option-section">
            <div className="frameselect-section-title">Photo Color</div>
            <div className="frameselect-option-buttons">
              <button className={`frameselect-option-button ${selectedPhotoColor === 'color1' ? 'selected' : ''}`} onClick={() => handleFrameSelect('photoColor', 'color1')}><img src={Color} alt="Color"></img></button>
              <button className={`frameselect-option-button ${selectedPhotoColor === 'color2' ? 'selected' : ''}`} onClick={() => handleFrameSelect('photoColor', 'color2')}><img src={BlackWhite} alt="Black and White"></img></button>
            </div>
          </div>
          <div className="frameselect-option-section">
            <div className="frameselect-section-header"><div className="frameselect-section-title">Special Frame</div><div className="frameselect-special-description">정말 특별한 사람들을 위한 프레임</div></div>
            <div className="frameselect-option-buttons">
              <button className={`frameselect-option-button ${selectedSpecialFrame === 'special1' ? 'selected' : ''}`} onClick={() => handleFrameSelect('specialFrame', 'special1')}><img src={FrameStar} alt="Star Frame"></img></button>
              <button className={`frameselect-option-button ${selectedSpecialFrame === 'special2' ? 'selected' : ''}`} onClick={() => handleFrameSelect('specialFrame', 'special2')}><img src={FrameOcean} alt="Ocean Frame"></img></button>
              <button className={`frameselect-option-button ${selectedSpecialFrame === 'special3' ? 'selected' : ''}`} onClick={() => handleFrameSelect('specialFrame', 'special3')}><img src={FrameShinguFun} alt="Shingu Fun Frame"></img></button>
            </div>
          </div>
          <div className="frameselect-option-section">
            <div className="frameselect-section-title">Frame</div>
            <div className="frameselect-option-buttons">
              <button className={`frameselect-option-button ${selectedFrame === 'frame1' ? 'selected' : ''}`} onClick={() => handleFrameSelect('frame', 'frame1')}><img src={FrameWhite} alt="White Frame"></img></button>
              <button className={`frameselect-option-button ${selectedFrame === 'frame2' ? 'selected' : ''}`} onClick={() => handleFrameSelect('frame', 'frame2')}><img src={FrameBlack} alt="Black Frame"></img></button>
              <button className={`frameselect-option-button ${selectedFrame === 'frame3' ? 'selected' : ''}`} onClick={() => handleFrameSelect('frame', 'frame3')}><img src={FrameParty} alt="Party Frame"></img></button>
              <button className={`frameselect-option-button ${selectedFrame === 'frame4' ? 'selected' : ''}`} onClick={() => handleFrameSelect('frame', 'frame4')}><img src={FrameZebra} alt="Zebra Frame"></img></button>
              <button className={`frameselect-option-button ${selectedFrame === 'frame5' ? 'selected' : ''}`} onClick={() => handleFrameSelect('frame', 'frame5')}><img src={FrameShingu} alt="Shingu Frame"></img></button>
            </div>
          </div>
        </div>
      </div>
      <div className="frameselect-back-button-container"><div className="frameselect-back-button" onClick={handleBack}><div className="frameselect-back-button-border"></div><div className="frameselect-back-text">BACK</div><div className="frameselect-back-arrow"><img alt="back arrow" src={BackArrow}/></div></div></div>
      <div className="frameselect-next-button-container"><div className="frameselect-next-button" onClick={handleNext}><div className="frameselect-next-button-border"></div><div className="frameselect-next-text">NEXT</div><div className="frameselect-next-arrow"><img alt="next arrow" src={NextArrow}/></div></div></div>
    </div>
  );
};

export default FrameSelect;