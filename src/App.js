import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

import MainPage from "./Mainpage";
import LoginPage from "./LoginPage";
import Mypage from "./Mypage";
import OAuthRedirectPage from "./OAuthRedirectPage";
import { AuthProvider } from "./AuthContext";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/Mypage" element={<Mypage />} />
            <Route path="/oauth-redirect" element={<OAuthRedirectPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
