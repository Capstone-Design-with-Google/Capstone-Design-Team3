import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [videoList, setVideoList] = useState([]);

  // 로그인 함수 (백엔드 연동 없이 간단하게)
  function login(userData) {
    setUser(userData);
  }

  // 로그아웃 함수
  function logout() {
    setUser(null);
  }

  function addVideo(video) {
    setVideoList(prev => [video, ...prev]);
  }

  const value = {
    user,
    login,
    logout,
    videoList,
    addVideo,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
