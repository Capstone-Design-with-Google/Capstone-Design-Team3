import React, { createContext, useContext, useState } from "react";
const AuthContext = createContext();

// export function useAuth() {
//   return useContext(AuthContext);
// }

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [videoList, setVideoList] = useState([]);

  // 로그인 함수 (백엔드 연동 없이 간단하게)
  // function login(userData) {
  //   setUser(userData);
  // }
   const login = (userInfo) => {
    setUser(userInfo);
    localStorage.setItem("user", JSON.stringify(userInfo));
  };
  // 로그아웃 함수
  // function logout() {
  //   setUser(null);
  // }
   const logout = () => {
    setUser(null);
    setVideoList([]);
    localStorage.removeItem("user");
  };
  // function addVideo(video) {
  //   setVideoList(prev => [video, ...prev]);
  // }
 const addVideo = (video) => {
    setVideoList((prev) => [...prev, video]);
  };
  // const value = {
  //   user,
  //   login,
  //   logout,
  //   videoList,
  //   addVideo,
  // };

  return (
    // <AuthContext.Provider value={value}>
    <AuthContext.Provider value={{ user, login, logout, videoList, addVideo }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export function useAuth() {
  return useContext(AuthContext);
}
