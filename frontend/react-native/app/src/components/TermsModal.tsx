import React, { useRef, useEffect } from 'react';
import { Modal, ScrollView, TouchableWithoutFeedback, Animated, Dimensions } from 'react-native';
import styled from 'styled-components/native';
import { MaterialIcons } from "@expo/vector-icons";
import { Platform } from 'react-native';

interface TermsModalProps {
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

const TermsModal = ({ isVisible, onClose, width }: TermsModalProps) => {
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
          <ModalTitle>야금야금 이용약관</ModalTitle>
          <CloseButton onPress={onClose}>
            <MaterialIcons name="close" size={24} color="#1B1D1F" />
          </CloseButton>
        </ModalHeader>
        
        <ContentContainer showsVerticalScrollIndicator={false}>
          <Section>
            <SectionTitle>제1조 (목적)</SectionTitle>
            <SectionText>
              이 약관은 야금야금(이하 "회사")이 제공하는 금융상품 및 관련 서비스(이하 "서비스")의 이용과 관련하여, 회사와 이용자 간의 권리, 의무 및 책임사항, 기타 필요한 사항을 규정함을 목적으로 합니다.
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>제2조 (정의)</SectionTitle>
            <SectionText>
              "이용자"란 본 약관에 동의하고 회사가 제공하는 서비스를 이용하는 자를 말합니다.{'\n\n'}
              "적금 상품"이란 일정 기간 동안 정기적으로 금액을 납입하고, 만기 시 원금 및 이자를 수령하는 금융상품을 말합니다.
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>제3조 (서비스의 내용 및 제공)</SectionTitle>
            <SectionText>
              회사는 다음과 같은 서비스를 제공합니다:{'\n\n'}
              • 적금 상품 가입, 해지, 관리 서비스{'\n'}
              • 적립금 이력 조회{'\n'}
              • 기타 금융 정보 제공 및 상담 서비스{'\n\n'}
              서비스 제공은 회사의 정책에 따라 변경될 수 있습니다.
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>제4조 (이용자의 의무)</SectionTitle>
            <SectionText>
              이용자는 서비스 이용 시 관련 법령 및 본 약관을 준수하여야 하며, 타인의 정보를 도용하거나 부정한 목적으로 서비스를 이용하여서는 안 됩니다.
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>제5조 (약관의 변경)</SectionTitle>
            <SectionText>
              회사는 관련 법령에 따라 본 약관을 변경할 수 있으며, 변경 시 사전 공지 후 적용합니다.
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

export default TermsModal; 