import React from "react";
import "./LoginPage.css";

function LoginPage() {
  const handleGoogleLogin = () => {
    // Spring Boot 백엔드의 OAuth2 로그인 시작 URL
    window.location.href = "http://localhost:8080/oauth2/authorization/google";
  };

  return (
    <div className="login-page">
      <h1 className="logo">
        SHOPPABLE<span className="highlight">.AI</span>
      </h1>
      <div className="login-container">
        <h2>로그인</h2>

        <div className="google-login">
          <button className="google-btn" onClick={handleGoogleLogin}>
            <img
              src="https://developers.google.com/identity/images/g-logo.png"
              alt="Google logo"
            />
            Sign in with Google
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
