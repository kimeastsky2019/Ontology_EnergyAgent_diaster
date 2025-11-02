import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  Home, 
  BarChart3, 
  Settings, 
  History, 
  AlertTriangle,
  TrendingUp,
  Cloud,
  Zap
} from 'lucide-react';

const SidebarContainer = styled.aside`
  position: fixed;
  left: 0;
  top: 0;
  width: 280px;
  height: 100vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 0;
  z-index: 200;
  overflow-y: auto;

  @media (max-width: 768px) {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
`;

const Logo = styled.div`
  padding: 0 2rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 2rem;
`;

const LogoText = styled.h1`
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Nav = styled.nav`
  padding: 0 1rem;
`;

const NavItem = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  margin: 0.25rem 0;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    transform: translateX(4px);
  }

  &.active {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 20px;
    background: linear-gradient(135deg, #4ade80, #22c55e);
    border-radius: 0 2px 2px 0;
  }
`;

const NavText = styled.span`
  font-weight: 500;
  font-size: 0.95rem;
`;

const SectionTitle = styled.h3`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 2rem 0 1rem 1.5rem;
`;

const StatusCard = styled.div`
  margin: 2rem 1rem 0;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const StatusTitle = styled.h4`
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 1rem;
`;

const StatusItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
`;

const StatusValue = styled.span`
  color: white;
  font-weight: 500;
`;

const Sidebar = () => {
  const navItems = [
    { icon: Home, text: 'Dashboard', active: true },
    { icon: BarChart3, text: 'Analytics', active: false },
    { icon: TrendingUp, text: 'Trends', active: false },
    { icon: Cloud, text: 'Weather Map', active: false },
    { icon: History, text: 'History', active: false },
    { icon: AlertTriangle, text: 'Alerts', active: false },
    { icon: Zap, text: 'Energy', active: false },
    { icon: Settings, text: 'Settings', active: false },
  ];

  return (
    <SidebarContainer>
      <Logo>
        <LogoText>
          <Cloud size={24} />
          WeatherPro
        </LogoText>
      </Logo>

      <Nav>
        {navItems.map((item, index) => (
          <NavItem
            key={index}
            className={item.active ? 'active' : ''}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <item.icon size={20} />
            <NavText>{item.text}</NavText>
          </NavItem>
        ))}
      </Nav>

      <StatusCard>
        <StatusTitle>System Status</StatusTitle>
        <StatusItem>
          <span>Data Source</span>
          <StatusValue>KMA API</StatusValue>
        </StatusItem>
        <StatusItem>
          <span>Update Rate</span>
          <StatusValue>5s</StatusValue>
        </StatusItem>
        <StatusItem>
          <span>Accuracy</span>
          <StatusValue>98.5%</StatusValue>
        </StatusItem>
        <StatusItem>
          <span>Last Update</span>
          <StatusValue>Now</StatusValue>
        </StatusItem>
      </StatusCard>
    </SidebarContainer>
  );
};

export default Sidebar;

