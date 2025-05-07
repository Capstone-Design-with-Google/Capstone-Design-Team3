import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './Mainpage.css';

function Mainpage() {
  const [url, setUrl] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState('');
  const { user, logout, addVideo } = useAuth();
  const navigate = useNavigate();

  // URL 제출 처리 (백엔드 연동 없이 상태 변경만)
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!user) {
      alert('로그인 후에 이용해주세요!');
      return;
    }
    
    setIsGenerating(true);
    
    // 백엔드 연동 없이 3초 후 가상 비디오 URL 생성
  //   setTimeout(() => {
  //     setVideoUrl('https://example.com/sample-video.mp4'); // 가상 비디오 URL
  //     setIsGenerating(false);
  //   }, 3000);
  // };
  setTimeout(() => {
    const newVideo = {
      id: Date.now(),
      title: `${url} 요약`,
      videoUrl: 'https://example.com/sample-video.mp4',
    };
    setVideoUrl(newVideo.videoUrl);
    setIsGenerating(false);
    addVideo(newVideo); // MyPage 목록에 추가
  }, 2000);
};

const handleLogout = () => {
  setUrl('');
  setIsGenerating(false);
  setVideoUrl('');
  logout();
  navigate('/');
};
  // 비디오 다운로드 처리
  const handleDownload = () => {
    // 실제로는 이곳에 비디오 다운로드 로직이 들어가야 함
    alert('다운로드 시작 (백엔드 없이 실제 다운로드는 되지 않습니다)');
  };

  return (
    <div className="main-page">
      <div className="header">
        {user ? (
           <div className="user-header">
           <span className="user-info">반갑습니다, {user.name}님</span>
           <div className="header-buttons">
             <button className="my-page-btn" onClick={() => navigate('/Mypage')}>
               MY PAGE
             </button>
             <button className="logout-btn" onClick={handleLogout}>
               LOGOUT
             </button>
           </div>
         </div>
      ) : (
        <button className="login-btn" onClick={() => navigate('/login')}>
          LOGIN
        </button>
      )}
      </div>
      
      <div className="content">
        <h1 className="logo">SHOPPABLE<span className="highlight">.AI</span></h1>
        
        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            className="search-input"
            placeholder="쇼핑 페이지 URL을 입력하세요"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button type="submit" className="search-button">
            SEARCH
          </button>
        </form>
        
        
        {/* {!user && (
          <div className="sign-in-section">
            <button className="google-login-btn" onClick={() => navigate('/login')}>
              <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" />
              Sign in with Google
            </button>
          </div>
        )} */}
        
        {isGenerating && (
          <div className="generating-message">
            <p>비디오 생성 중...</p>
          </div>
        )}
        
        {videoUrl && !isGenerating && (
          <div className="video-result">
            <div className="video-player">
              <p>비디오가 생성되었습니다!</p>
            </div>
            <button className="download-btn" onClick={handleDownload}>
              비디오 다운로드
            </button>
          </div>
        )}
        
        {/* <div className="recommended-section">
          <h3>TOP 3 recommended</h3>
          <div className="recommended-items">
            <div className="recommended-item">
              <img src="https://via.placeholder.com/150" alt="준마라탕" />
              <p>준마라탕</p>
            </div>
            <div className="recommended-item">
              <img src="https://via.placeholder.com/150" alt="스시마라" />
              <p>스시마라</p>
            </div>
            <div className="recommended-item">
              <img src="https://via.placeholder.com/150" alt="마라XX" />
              <p>마라XX</p>
            </div>
          </div>
        </div> */}
      </div>
    </div>
  );
}

export default Mainpage;
