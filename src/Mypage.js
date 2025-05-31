import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './Mypage.css';

function MyPage() {
  const { videoList, user } = useAuth();
  
  const navigate = useNavigate();

  const downloadVideo = (url) => {
    alert("다운로드 시작! (실제 다운로드는 백엔드 연동 시 구현됩니다)");
  };

  const handleGoHome = () => {
    navigate("/");
  };

  return (
    <div className="mypage">
      {/* 헤더 영역 */}
      <div className="mypage-header">
        <button className="home-btn" onClick={handleGoHome}>
          HOME
        </button>
      </div>
      {/* 사용자 이름 출력 */}
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
        // <ul>
        //   {videoList.map(video => (
        //     <li key={video.id} style={{ marginBottom: '10px' }}>
        ////////////////////////////////////
        // <ul className="video-list">
        //   {videoList.map((video) => (
        //     <li key={video.id} className="video-item">
        //       <span>{video.title}</span>
        //       <button onClick={() => downloadVideo(video.videoUrl)}>
        //         {video.title}
        //         다운로드
        //       </button>
        //     </li>
        //   ))}
        // </ul>
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
