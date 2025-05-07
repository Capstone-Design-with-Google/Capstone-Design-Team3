import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './LoginPage.css';

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  // 구글 로그인 처리 (백엔드 연동 없이 간단하게)
  const handleGoogleLogin = () => {
    // 가상의 사용자 데이터
    const userData = {
      id: 'user123',
      name: '홍길동',
      email: 'user@example.com'
    };
    
    login(userData);
    navigate('/');
  };

  return (
    <div className="login-page">
      <h1 className="logo">SHOPPABLE<span className="highlight">.AI</span></h1>
      <div className="login-container">
        <h2>로그인</h2>
        
        <div className="google-login">
          <button className="google-btn" onClick={handleGoogleLogin}>
            <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" />
            Sign in with Google
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
