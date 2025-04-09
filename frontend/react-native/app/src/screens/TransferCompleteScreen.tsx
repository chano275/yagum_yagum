import React from 'react';
import { View, useWindowDimensions, Platform } from 'react-native';
import styled from 'styled-components/native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { BASE_MOBILE_WIDTH, MAX_MOBILE_WIDTH } from '../constants/layout';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAccountStore } from '../store/useStore';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/AppNavigator';

interface StyledProps {
  width: number;
  insetsTop?: number;
}

const TransferCompleteScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const { width: windowWidth } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const { fetchAccountInfo } = useAccountStore();
  
  const width = Platform.OS === 'web' 
    ? BASE_MOBILE_WIDTH 
    : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  const handleConfirm = async () => {
    await fetchAccountInfo(); // 계좌 정보 새로고침
    navigation.navigate('Home');
  };

  return (
    <Container>
      <MobileContainer width={width} insetsTop={insets.top}>
        <ContentContainer>
          <IconContainer>
            <Ionicons name="checkmark" size={66} color="#FFFFFF" />
          </IconContainer>
          <CompleteText>이체 완료</CompleteText>
        </ContentContainer>
        <BottomButtonContainer>
          <ConfirmButton onPress={handleConfirm}>
            <ButtonText>확인</ButtonText>
          </ConfirmButton>
        </BottomButtonContainer>
      </MobileContainer>
    </Container>
  );
};

const Container = styled.View`
  flex: 1;
  align-items: center;
  background-color: white;
`;

const MobileContainer = styled.View<StyledProps>`
  width: ${({ width }) => width}px;
  max-width: 100%;
  flex: 1;
  align-self: center;
  overflow: hidden;
  position: relative;
  background-color: white;
  padding-top: ${props => props.insetsTop || 0}px;
`;

const ContentContainer = styled.View`
  flex: 1;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
  padding-bottom: 160px;
`;

const IconContainer = styled.View`
  width: 110px;
  height: 110px;
  border-radius: 55px;
  background-color: #2D5BFF;
  justify-content: center;
  align-items: center;
  margin-bottom: 32px;
`;

const CompleteText = styled.Text`
  font-size: 32px;
  font-weight: 600;
  color: #000000;
`;

const BottomButtonContainer = styled.View`
  width: 100%;
  padding: 0 20px;
  padding-bottom: 20px;
  margin-top: auto;
`;

const ConfirmButton = styled.TouchableOpacity`
  background-color: #2D5BFF;
  padding: 16px;
  border-radius: 12px;
  align-items: center;
  width: 100%;
`;

const ButtonText = styled.Text`
  color: white;
  font-size: 16px;
  font-weight: 600;
`;

export default TransferCompleteScreen; 