import { type FC } from 'react';
import type { Theme } from '@mui/material/styles';
import type { HTMLMotionProps } from 'framer-motion';
import { Box, Typography, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

const CalendarGrid = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(7, 1fr)',
  gap: theme.spacing(1),
  marginTop: theme.spacing(2),
}));

const DayCell = styled(motion(Paper))<{ completed?: boolean; theme?: Theme }>(({ theme, completed }) => ({
  aspectRatio: '1',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: completed ? theme.palette.primary.main : theme.palette.background.paper,
  color: completed ? theme.palette.primary.contrastText : theme.palette.text.secondary,
  border: `1px solid ${theme.palette.divider}`,
  cursor: 'pointer',
  position: 'relative',
  overflow: 'hidden',
}));

interface StreakCalendarProps {
  weeklyStats: Array<{
    date: string;
    day: string;
    minutes: number;
    sessions: number;
  }>;
}

const StreakCalendar: FC<StreakCalendarProps> = ({ weeklyStats }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  };

  const cellVariants = {
    hidden: { scale: 0.8, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 25
      }
    }
  };

  return (
    <Box>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        Last 7 Days
      </Typography>
      
      <CalendarGrid>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          style={{ display: 'contents' }}
          {...({} as HTMLMotionProps<"div">)}
        >
        {weeklyStats.map((day, index) => (
          <DayCell
            key={day.date}
            completed={day.minutes > 0}
            variants={cellVariants}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" display="block">
                {day.day}
              </Typography>
              {day.minutes > 0 && (
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontSize: '0.7rem',
                    opacity: 0.8 
                  }}
                >
                  {day.minutes}m
                </Typography>
              )}
            </Box>
            {day.minutes > 0 && (
              <Box
                component={motion.div}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  background: (theme) => `linear-gradient(135deg, 
                    ${theme.palette.primary.light}20 0%, 
                    ${theme.palette.primary.main}40 100%)`,
                  zIndex: 0,
                }}
              />
            )}
          </DayCell>
        ))}
        </motion.div>
      </CalendarGrid>
    </Box>
  );
};

export default StreakCalendar;
