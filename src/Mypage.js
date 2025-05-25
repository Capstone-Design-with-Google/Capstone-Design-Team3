import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './Mypage.css';

function MyPage() {
  const { videoList, user } = useAuth();
  const navigate = useNavigate();

  // 비디오 다운로드 함수(더미)
  const downloadVideo = (url) => {
    alert('다운로드 시작 (백엔드 없이 실제 다운로드는 되지 않습니다)');
  };

  // Home 버튼 클릭 시 메인페이지로 이동
  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="mypage">
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
        <ul className="video-list">
          {videoList.map((video) => (
            <li key={video.id} className="video-item">
              <span>{video.title}</span>
              <button onClick={() => downloadVideo(video.videoUrl)}>
                {video.title}
                다운로드드
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MyPage;
