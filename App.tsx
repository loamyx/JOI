
import React, { type FC } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { StreakProvider } from './contexts/StreakContext';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from './styles/theme';
import Layout from './components/Layout';
import Home from './pages/Home';
import Meditation from './pages/Meditation';
import Profile from './pages/Profile';
import Social from './pages/Social';
import Auth from './pages/Auth';

const App: FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <StreakProvider>
          <Layout>
            <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/meditation" element={<Meditation />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/social" element={<Social />} />
            <Route path="/auth" element={<Auth />} />
            </Routes>
          </Layout>
        </StreakProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
