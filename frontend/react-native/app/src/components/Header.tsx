import React, { useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, Animated, Platform } from 'react-native';
import styled from 'styled-components/native';
import { MaterialIcons } from '@expo/vector-icons';
import { useTeam } from '../context/TeamContext';

interface HeaderProps {
  title: string;
  step?: number;
  totalSteps?: number;
  showProgress?: boolean;
  onBack?: () => void;
}

interface ProgressFillProps {
  color: string;
  step: number;
  totalSteps: number;
}

const HeaderContainer = styled.View`
  width: 100%;
  background-color: white;
`;

const HeaderTop = styled.View`
  width: 100%;
  height: 60px;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  background-color: white;
  position: relative;
`;

const BackButton = styled.TouchableOpacity`
  position: absolute;
  left: 14px;
  width: 28px;
  height: 28px;
  justify-content: center;
  align-items: center;
`;

const HeaderTitle = styled.Text`
  font-size: 20px;
  font-weight: 700;
  color: #222222;
`;

const PageNumber = styled.Text`
  position: absolute;
  right: 20px;
  font-size: 14px;
  color: #666666;
  font-weight: 400;
`;

const ProgressBar = styled.View`
  width: calc(100% - 40px);
  margin: 0 20px;
  height: 2px;
  background-color: #EEEEEE;
  border-radius: 1px;
  overflow: hidden;
`;

const ProgressFill = styled(Animated.View)<ProgressFillProps>`
  width: 100%;
  height: 100%;
  background-color: ${({ color }) => color};
  border-radius: 1px;
`;

const Header: React.FC<HeaderProps> = ({
  title,
  step = 1,
  totalSteps = 4,
  showProgress = true,
  onBack
}) => {
  const progressAnim = useRef(new Animated.Value(0)).current;
  const { teamColor } = useTeam();

  useEffect(() => {
    if (showProgress) {
      Animated.timing(progressAnim, {
        toValue: step / totalSteps,
        duration: 500,
        useNativeDriver: false,
      }).start();
    }
  }, [step, totalSteps, showProgress]);

  return (
    <HeaderContainer>
      <HeaderTop>
        <BackButton onPress={onBack}>
          <MaterialIcons name="chevron-left" size={24} color="#666" />
        </BackButton>
        <HeaderTitle>{title}</HeaderTitle>
        {showProgress && <PageNumber>{step}/{totalSteps}</PageNumber>}
      </HeaderTop>
      {showProgress && (
        <ProgressBar>
          <ProgressFill 
            style={{
              transform: [{
                translateX: progressAnim.interpolate({
                  inputRange: [0, 1],
                  outputRange: ['-100%', '0%']
                })
              }]
            }}
            step={step}
            totalSteps={totalSteps}
            color={teamColor.primary}
          />
        </ProgressBar>
      )}
    </HeaderContainer>
  );
};

export default Header;
