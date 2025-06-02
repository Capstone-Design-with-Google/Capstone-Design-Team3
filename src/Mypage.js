import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './Mypage.css';
import axios from 'axios';

function MyPage() {
  const { videoList, user } = useAuth();
  const navigate = useNavigate();

  // 실제 다운로드 구현
  const downloadVideo = async (videoUrl) => {
    try {
      const fullUrl = videoUrl.startsWith("http")
        ? videoUrl
        : `http://localhost:5000${videoUrl}`;

      const response = await axios.get(fullUrl, {
        responseType: "blob",
        withCredentials: true,
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `video_${Date.now()}.mp4`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Download error:", error);
      alert("다운로드 중 오류가 발생했습니다.");
    }
  };

  const handleGoHome = () => {
    navigate("/");
  };

  return (
    <div className="mypage">
      <div className="mypage-header">
        <button className="home-btn" onClick={handleGoHome}>
          HOME
        </button>
      </div>

      {user && (
        <div className="user-greeting">
          <p>
            <strong>{user.name}</strong>님의 영상 목록
          </p>
        </div>
      )}
      <h1>My Videos</h1>

      {videoList.length === 0 ? (
        <p>생성된 영상이 없습니다.</p>
      ) : (
        <ul className="video-list">
          {videoList.map((video, idx) => (
            <li key={video.id} className="video-item">
              <button
                className="home-btn big-center-btn"
                onClick={() => downloadVideo(video.videoUrl)}
              >
                my video {idx + 1} download
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MyPage;
