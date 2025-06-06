import React, { createContext, useContext, useState } from "react";
const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [videoList, setVideoList] = useState([]);

   const login = (userInfo) => {
    setUser(userInfo);
    localStorage.setItem("user", JSON.stringify(userInfo));
  };
 
   const logout = () => {
    setUser(null);
    setVideoList([]);
    localStorage.removeItem("user");
  };

 const addVideo = (video) => {
    setVideoList((prev) => [...prev, video]);
  };

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
