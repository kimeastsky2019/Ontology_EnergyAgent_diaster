import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

const ErrorContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
`;

const ErrorIcon = styled(motion.div)`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
  border: 2px solid rgba(239, 68, 68, 0.3);
`;

const ErrorTitle = styled(motion.h1)`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: white;
`;

const ErrorMessage = styled(motion.p)`
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
  max-width: 600px;
  line-height: 1.6;
`;

const ErrorActions = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`;

const ErrorButton = styled(motion.button)`
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  background: ${props => props.primary ? 'linear-gradient(135deg, #4ade80, #22c55e)' : 'rgba(255, 255, 255, 0.1)'};
  color: white;
  border: 1px solid ${props => props.primary ? 'transparent' : 'rgba(255, 255, 255, 0.2)'};

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  }
`;

const ErrorDetails = styled(motion.details)`
  margin-top: 2rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 1rem;
  max-width: 600px;
  text-align: left;
`;

const ErrorSummary = styled.summary`
  cursor: pointer;
  font-weight: 600;
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.9);
`;

const ErrorCode = styled.pre`
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #ef4444;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
`;

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleRefresh = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorContainer>
          <ErrorIcon
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.5 }}
          >
            <AlertTriangle size={40} color="#ef4444" />
          </ErrorIcon>

          <ErrorTitle
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            Oops! Something went wrong
          </ErrorTitle>

          <ErrorMessage
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            We encountered an unexpected error while loading the weather data. 
            This might be due to a network issue or a temporary service problem.
          </ErrorMessage>

          <ErrorActions>
            <ErrorButton
              primary
              onClick={this.handleRefresh}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw size={20} />
              Try Again
            </ErrorButton>
            <ErrorButton
              onClick={this.handleGoHome}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Home size={20} />
              Go Home
            </ErrorButton>
          </ErrorActions>

          {this.state.error && (
            <ErrorDetails
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <ErrorSummary>Technical Details</ErrorSummary>
              <ErrorCode>
                {this.state.error && this.state.error.toString()}
                {this.state.errorInfo.componentStack}
              </ErrorCode>
            </ErrorDetails>
          )}
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;







