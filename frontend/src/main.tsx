import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import App from './App.tsx';
import VerifyEmail from './components/VerifyEmail.tsx';
import ForgotPassword from './components/ForgotPassword.tsx';
import ResetPassword from './components/ResetPassword.tsx';
import { AuthProvider } from './hooks/authContext';

// Create Router component
const Router = () => {
  // Dark mode state (shared across components)
  const [isDarkMode, setIsDarkMode] = React.useState(false);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/login" element={<App />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/forgot-password" element={
        <ForgotPassword isDarkMode={isDarkMode} />
      } />
      <Route path="/reset-password" element={
        <ResetPassword isDarkMode={isDarkMode} />
      } />
    </Routes>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Router />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);