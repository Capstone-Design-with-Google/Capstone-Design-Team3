import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './AuthContext';

function OAuthRedirectPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    axios
      .get('http://localhost:8080/api/user', { withCredentials: true })
      .then((res) => {
        login(res.data);
        navigate('/');
      })
      .catch(() => {
        alert('로그인 실패');
        navigate('/login');
      });
  }, [navigate, login]);

  return <div>로그인 처리 중...</div>;
}

export default OAuthRedirectPage;