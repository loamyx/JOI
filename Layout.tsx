import React, { ReactNode } from 'react';
import { Box, AppBar, Toolbar, IconButton, Typography, Container, Paper } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import SelfImprovementIcon from '@mui/icons-material/SelfImprovement';
import PersonIcon from '@mui/icons-material/Person';
import PeopleIcon from '@mui/icons-material/People';
import { motion } from 'framer-motion';

const MotionPaper = motion(Paper);

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: <HomeIcon />, path: '/', label: 'Home' },
    { icon: <SelfImprovementIcon />, path: '/meditation', label: 'Meditate' },
    { icon: <PeopleIcon />, path: '/social', label: 'Social' },
    { icon: <PersonIcon />, path: '/profile', label: 'Profile' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          bgcolor: 'background.paper',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              flexGrow: 1,
              color: 'text.primary',
              fontWeight: 600
            }}
          >
            JOI
          </Typography>
        </Toolbar>
      </AppBar>

      <Container 
        maxWidth="sm" 
        sx={{ 
          pt: 10, 
          pb: 9,
          height: '100%',
        }}
      >
        {children}
      </Container>

      <Paper
        elevation={0}
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-around' }}>
          {navItems.map((item) => (
            <IconButton
              key={item.path}
              onClick={() => navigate(item.path)}
              sx={{
                color: location.pathname === item.path ? 'primary.main' : 'text.secondary',
                display: 'flex',
                flexDirection: 'column',
                gap: 0.5,
              }}
            >
              {item.icon}
              <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>
                {item.label}
              </Typography>
              {location.pathname === item.path && (
                <MotionPaper
                  layoutId="nav-indicator"
                  initial={false}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  sx={{
                    position: 'absolute',
                    bottom: -8,
                    height: 4,
                    width: 20,
                    bgcolor: 'primary.main',
                    borderRadius: 2,
                  }}
                />
              )}
            </IconButton>
          ))}
        </Toolbar>
      </Paper>
    </Box>
  );
};

export default Layout;
