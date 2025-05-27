import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import "./Mainpage.css";


function Mainpage() {
  const [url, setUrl] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");

  const { user, logout, addVideo } = useAuth();
  const navigate = useNavigate();

  // URL 제출 처리 (백엔드 연동 없이 상태 변경만)
  // 제출 시 URL 기반 비디오 생성 흐름
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
    const response = await fetch('/api/receive-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error('서버 오류: ' + response.status);
    }

    // 백엔드에서 결과 데이터 받기 (예: 영상 URL 등)
    const data = await response.text();
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
//백에 url 전달 구현 전//
//   setTimeout(() => {
//     const newVideo = {
//       id: Date.now(),
//       title: `${url} 요약`,
//       videoUrl: 'https://example.com/sample-video.mp4',
//     };
//     setVideoUrl(newVideo.videoUrl);

//     setIsGenerating(false);
//     addVideo(newVideo); // MyPage 목록에 추가
//   }, 2000);
// };

  const handleLogout = () => {
    setUrl("");
    setIsGenerating(false);
    setVideoUrl("");
    logout();
    navigate("/");
  };

  const handleDownload = () => {
    alert("비디오 다운로드는 실제 백엔드 연동 시 구현됩니다.");
  };

  return (
    <div className="main-page">
      {/* 상단 헤더 */}
      <div className="header">
        {user ? (
          <div className="user-header">
            <span className="user-info">반갑습니다, {user.name}님</span>
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
              <p>비디오가 생성되었습니다!</p>
              {/* 여기에 video 태그나 player 넣을 수도 있음 */}
            </div>
            <button className="download-btn" onClick={handleDownload}>
              비디오 다운로드
            </button>
          </div>
        )}
        
      </div>
    </div>
  );
}

export default Mainpage;
