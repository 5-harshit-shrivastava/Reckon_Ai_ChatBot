import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { reckonTheme } from './shared';
import DashboardPage from './pages/DashboardPage';
import DataManagementPage from './pages/DataManagementPage';

function App() {
  return (
    <ThemeProvider theme={reckonTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/data" element={<DataManagementPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
