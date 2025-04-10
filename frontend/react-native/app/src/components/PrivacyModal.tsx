import React, { useRef, useEffect } from 'react';
import { Modal, ScrollView, TouchableWithoutFeedback, Platform, Animated, Dimensions } from 'react-native';
import styled from 'styled-components/native';
import { MaterialIcons } from "@expo/vector-icons";

interface PrivacyModalProps {
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

const PrivacyModal = ({ isVisible, onClose, width }: PrivacyModalProps) => {
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
          <ModalTitle>개인정보 수집 및 이용 동의</ModalTitle>
          <CloseButton onPress={onClose}>
            <MaterialIcons name="close" size={24} color="#1B1D1F" />
          </CloseButton>
        </ModalHeader>
        
        <ContentContainer showsVerticalScrollIndicator={false}>
          <Section>
            <SectionTitle>1. 수집 항목</SectionTitle>
            <SectionText>
              성명, 생년월일, 성별, 연락처, 이메일{`\n`}
              계좌정보, 거래 내역 등 금융정보{`\n`}
              접속 로그, 쿠키, IP 정보 등
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>2. 수집 목적</SectionTitle>
            <SectionText>
              적금 상품 가입 및 계약 이행{`\n`}
              본인 확인 및 고객 서비스 제공{`\n`}
              법령상 의무 준수 (예: 고객확인제도 등)
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>3. 보유 및 이용 기간</SectionTitle>
            <SectionText>
              수집일로부터 서비스 종료 또는 계약 해지 후 5년까지 보관 (관련 법령에 따라 달라질 수 있음)
            </SectionText>
          </Section>

          <Section>
            <SectionTitle>4. 동의 거부권 및 불이익</SectionTitle>
            <SectionText>
              고객은 동의를 거부할 권리가 있으나, 거부 시 적금 서비스 이용이 제한될 수 있습니다.
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

export default PrivacyModal; 