import { useState, useEffect } from 'react';
import { Box, Typography, IconButton, CircularProgress } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import styled from '@emotion/styled';

const TimerContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
`;

const ProgressContainer = styled(Box)`
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 200px;
`;

const TimeDisplay = styled(Typography)`
  position: absolute;
  font-size: 2rem;
  font-weight: 300;
`;

interface MeditationTimerProps {
  duration: number;
  onComplete: () => void;
}

const MeditationTimer = ({ duration, onComplete }: MeditationTimerProps) => {
  const [timeLeft, setTimeLeft] = useState(duration);
  const [isRunning, setIsRunning] = useState(false);
  const progress = ((duration - timeLeft) / duration) * 100;

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isRunning && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setIsRunning(false);
            onComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isRunning, timeLeft, onComplete]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  return (
    <TimerContainer
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <ProgressContainer>
        <CircularProgress
          variant="determinate"
          value={progress}
          size={200}
          thickness={2}
          sx={{
            color: (theme) => theme.palette.primary.main,
            opacity: 0.2,
          }}
        />
        <CircularProgress
          variant="determinate"
          value={progress}
          size={200}
          thickness={2}
          sx={{
            position: 'absolute',
            color: (theme) => theme.palette.primary.main,
            animation: 'none',
          }}
        />
        <TimeDisplay variant="h2">{formatTime(timeLeft)}</TimeDisplay>
      </ProgressContainer>

      <Box mt={3}>
        <IconButton
          onClick={toggleTimer}
          sx={{
            backgroundColor: (theme) => theme.palette.primary.main,
            color: 'white',
            '&:hover': {
              backgroundColor: (theme) => theme.palette.primary.dark,
            },
            width: 64,
            height: 64,
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={isRunning ? 'pause' : 'play'}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              transition={{ duration: 0.2 }}
            >
              {isRunning ? <PauseIcon /> : <PlayArrowIcon />}
            </motion.div>
          </AnimatePresence>
        </IconButton>
      </Box>
    </TimerContainer>
  );
};

export default MeditationTimer;
