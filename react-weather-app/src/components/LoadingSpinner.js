import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
`;

const Spinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: 2rem;
`;

const LoadingText = styled(motion.div)`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const LoadingSubtext = styled(motion.div)`
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  max-width: 300px;
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const Dot = styled(motion.div)`
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
`;

const LoadingSpinner = () => {
  return (
    <LoadingContainer>
      <Spinner />
      <LoadingText
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        Loading Weather Data
      </LoadingText>
      <LoadingSubtext
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        Fetching real-time weather information and analytics...
      </LoadingSubtext>
      <LoadingDots>
        {[0, 1, 2].map((index) => (
          <Dot
            key={index}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: index * 0.2,
            }}
          />
        ))}
      </LoadingDots>
    </LoadingContainer>
  );
};

export default LoadingSpinner;







