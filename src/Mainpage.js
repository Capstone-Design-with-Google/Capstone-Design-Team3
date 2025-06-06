import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import "./Mainpage.css";
//import axios from 'axios';

function Mainpage() {
  const [url, setUrl] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const { user, logout, addVideo } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!user) {
      alert('로그인 후에 이용해주세요!');
      return;
    }
    if (!url.trim()) {
      alert("URL을 입력해주세요.");
      return;
    }
    setIsGenerating(true);
    try {
    // 백엔드로 URL 전달 (POST 요청)
    const response = await fetch('http://localhost:5000/api/receive-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
      credentials: 'include', // 세션 인증 필요
  });


    if (!response.ok) {
      throw new Error('서버 오류: ' + response.status);
    }

    // 백엔드에서 결과 데이터 받기 (예: 영상 URL 등)
    const data = await response.json(); 
    // 반환
    // 예시: data.videoUrl이 백엔드에서 반환된다면
    const newVideo = {
      id: Date.now(),
      title: `${url} 요약`,
      videoUrl: data.videoUrl || 'https://example.com/sample-video.mp4',
    };
    setVideoUrl(newVideo.videoUrl);
    addVideo(newVideo); // MyPage 목록에 추가
  } catch (err) {
    alert('서버와 통신 중 오류가 발생했습니다: ' + err.message);
  } finally {
    setIsGenerating(false);
  }
};

  const handleLogout = () => {
  fetch("http:localhost:5000/logout", { credentials: "include" })
    .then(() => {
      setUrl("");
      setIsGenerating(false);
      setVideoUrl("");
      logout();
      navigate("/");
    });
};

useEffect(() => {
    localStorage.setItem("lastUrl", url);
  }, [url]);

  useEffect(() => {
    localStorage.setItem("lastVideoUrl", videoUrl);
  }, [videoUrl]);

  return (
    <div className="main-page">
      {/* 상단 헤더 */}
      <div className="header">
        {user ? (
          <div className="user-header">
            <span className="user-info"><strong>반갑습니다, {user.name}님</strong></span>
            <div className="header-buttons">
              <button
                className="my-page-btn"
                onClick={() => navigate("/Mypage")}
              >
                MY PAGE
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                LOGOUT
              </button>
            </div>
          </div>
        ) : (
          <button className="login-btn" onClick={() => navigate("/login")}>
            LOGIN
          </button>
        )}
      </div>

      {/* 본문 내용 */}
      <div className="content">
        
        <h1 className="logo">
          SHOPPABLE<span className="highlight">.AI</span>
        </h1>

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
        
        {isGenerating && (
          <div className="generating-message">
            <p>비디오 생성 중...</p>
          </div>
        )}

        {videoUrl && !isGenerating && (
          <div className="video-result">
            <div className="video-player">
              <p className="video-success-msg">
                비디오가 생성되었습니다!
              </p>
              <video
                src={`http://localhost:5000${videoUrl}`}
                controls
                width="250"
                height="250"
                style={{ margin: '10px 0', objectFit: 'contain', borderRadius: '12px', background: '#000' }}
              />
              <div className="download-info">
                영상 다운로드는 MY PAGE에서 할 수 있습니다
              </div>
            </div>
          </div>
        )}
        
      </div>
    </div>
  );
}

export default Mainpage;
