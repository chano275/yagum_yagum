import React, { useRef, useEffect } from 'react';
import { Modal, Animated, Dimensions, Platform } from 'react-native';
import styled from 'styled-components/native';
import { MaterialIcons } from "@expo/vector-icons";

interface MarketingModalProps {
  isVisible: boolean;
  onClose: () => void;
  width: number;
}

interface StyledProps {
  width: number;
}

const Backdrop = styled.Pressable`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
`;

const ModalContainer = styled(Animated.View)<StyledProps>`
  position: absolute;
  bottom: 0;
  left: ${props => (Dimensions.get('window').width - props.width) / 2}px;
  width: ${props => props.width}px;
  background-color: white;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  padding: 24px 20px;
  max-height: 80%;
`;

const ModalHeader = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.Text`
  font-size: 18px;
  font-weight: 600;
  color: #1b1d1f;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const CloseButton = styled.TouchableOpacity`
  padding: 8px;
`;

const ContentContainer = styled.ScrollView`
  max-height: 500px;
`;

const Section = styled.View`
  margin-bottom: 24px;
`;

const SectionTitle = styled.Text`
  font-size: 16px;
  font-weight: 600;
  color: #1b1d1f;
  margin-bottom: 12px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const SectionText = styled.Text`
  font-size: 14px;
  color: #666666;
  line-height: 20px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const BottomButton = styled.TouchableOpacity`
  background-color: #1a1a1a;
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  margin-top: 16px;
`;

const ButtonText = styled.Text`
  color: white;
  font-size: 16px;
  font-weight: 600;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const MarketingModal = ({ isVisible, onClose, width }: MarketingModalProps) => {
  const slideAnim = useRef(new Animated.Value(0)).current;
  const { height } = Dimensions.get('window');

  useEffect(() => {
    if (isVisible) {
      Animated.spring(slideAnim, {
        toValue: 1,
        tension: 65,
        friction: 11,
        useNativeDriver: true,
      }).start();
    } else {
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [isVisible]);

  const translateY = slideAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [height, 0],
  });

  return (
    <Modal
      visible={isVisible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <Backdrop onPress={onClose} />
      <ModalContainer width={width} style={{ transform: [{ translateY }] }}>
        <ModalHeader>
          <ModalTitle>마케팅 정보 수신 동의</ModalTitle>
          <CloseButton onPress={onClose}>
            <MaterialIcons name="close" size={24} color="#1B1D1F" />
          </CloseButton>
        </ModalHeader>
        
        <ContentContainer showsVerticalScrollIndicator={false}>
          <Section>
            <SectionTitle>1. 수신 항목</SectionTitle>
            <SectionText>
              이메일, 문자(SMS/MMS), 앱 푸시 등
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>2. 이용 목적</SectionTitle>
            <SectionText>
              신규 상품, 이벤트, 프로모션 안내{'\n\n'}
              고객 맞춤형 서비스 제공을 위한 설문 및 분석
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>3. 보유 및 이용 기간</SectionTitle>
            <SectionText>
              동의일로부터 철회 시점 또는 2년까지
            </SectionText>
          </Section>
        </ContentContainer>

        <BottomButton onPress={onClose}>
          <ButtonText>확인</ButtonText>
        </BottomButton>
      </ModalContainer>
    </Modal>
  );
};

export default MarketingModal; 