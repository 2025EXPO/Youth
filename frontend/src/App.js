import React, { useState, useEffect } from 'react';
import MainNoon from './codes/js/MainNoon';
import NumSelect from './codes/js/NumSelect';
import Start from './codes/js/Start';
import PhotoShoot from './codes/js/PhotoShoot';
import PhotoSelect from './codes/js/PhotoSelect';
import FrameSelect from './codes/js/FrameSelect';
import QR from './codes/js/QR'; // 마지막 QR 페이지 컴포넌트를 import 합니다.
import './App.css';

function App() {
  const [page, setPage] = useState('main');
  const [quantity, setQuantity] = useState(0); 
  const [takenPhotos, setTakenPhotos] = useState([]);
  const [selectedPhotos, setSelectedPhotos] = useState([]);
  // 사용자가 선택한 프레임 옵션을 저장할 새로운 state를 추가합니다.
  const [frameOptions, setFrameOptions] = useState(null);

  useEffect(() => {
    console.log(`App.js:20 페이지 변경: ${page}`);
  }, [page]);

  const renderPage = () => {
    switch (page) {
      case 'main':
        return <MainNoon onStartClick={() => setPage('numSelect')} />;
      case 'numSelect':
        return <NumSelect 
          onNext={(num) => {
            setQuantity(num);
            console.log(`App.js:39 NumSelect 완료, 수량: ${num}`);
            setPage('start');
          }}
          onBack={() => setPage('main')} 
        />;
      case 'start':
        return <Start onComplete={() => setPage('photoShoot')} />;
      case 'photoShoot':
        return <PhotoShoot onComplete={(photos) => {
          console.log('App.js:45 PhotoShoot 완료, 사진 목록 받음:', photos);
          setTakenPhotos(photos);
          setPage('photoSelect');
        }} />;
      case 'photoSelect':
        return <PhotoSelect
          photos={takenPhotos}
          onComplete={(photos) => {
            console.log('App.js:51 PhotoSelect 완료, 선택된 사진:', photos);
            setSelectedPhotos(photos);
            setPage('frameSelect');
          }}
          onBack={() => setPage('photoShoot')}
        />;
      case 'frameSelect':
  
        return <FrameSelect
          selectedPhotos={selectedPhotos}
          onComplete={(options) => {
            console.log('App.js: FrameSelect 완료, 선택된 옵션:', options);
            setFrameOptions(options); // 선택된 옵션을 state에 저장
            setPage('qr'); // 마지막 'qr' 페이지로 이동
          }}
          onBack={() => setPage('photoSelect')}
        />;
      case 'qr':
        // 최종 QR 페이지를 렌더링합니다. (다음 단계에서 구현)
        return <QR />;
      default:
        return <MainNoon onStartClick={() => setPage('numSelect')} />;
    }
  };

  return (
    <div className="App">
      {renderPage()}
    </div>
  );
}

export default App;