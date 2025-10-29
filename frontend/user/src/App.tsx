import React from 'react';
// FORCE REBUILD - API URL FIX - 2025-10-30
import { ThemeProvider, CssBaseline } from '@mui/material';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { reckonTheme } from './shared';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <ThemeProvider theme={reckonTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
