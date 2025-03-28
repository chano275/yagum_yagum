import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, SafeAreaView, Platform, useWindowDimensions, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AppWrapper, MobileContainer, getAdjustedWidth } from '../constants/layout';
import styled from 'styled-components/native';

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  SavingsJoin: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList>;

interface StyledProps {
  width: number;
}

const Content = styled.View`
  flex: 1;
  background-color: #fff;
`;

const TitleContainer = styled.View`
  flex-direction: row;
  align-items: center;
  padding-vertical: 12px;
  background-color: rgba(192, 238, 242, 0.2);
  width: 100%;
`;

const BackButton = styled.TouchableOpacity`
  padding: 8px;
`;

const Title = styled.Text`
  font-weight: bold;
  flex: 1;
  text-align: center;
  margin-right: 32px;
  color: #000;
  font-size: 20px;
`;

const TagContainer = styled.View`
  flex-direction: row;
  margin-bottom: 32px;
  justify-content: center;
  gap: 12px;
  padding-vertical: 16px;
`;

const Tag = styled.Text`
  color: #666;
  font-size: 15px;
  font-weight: 500;
`;

const TopSection = styled.View`
  background-color: rgba(192, 238, 242, 0.2);
  width: 100%;
  padding-horizontal: 20px;
  margin-top: -16px;
`;

const InfoBox = styled.View`
  flex-direction: row;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 12px;
`;

const InfoColumn = styled.View`
  flex: 1;
  align-items: center;
`;

const CardIconPlaceholder = styled.View`
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  background-color: #fff;
  border-radius: 24px;
`;

const InfoTitle = styled.Text`
  font-size: 15px;
  color: #666;
  margin-bottom: 8px;
`;

const InfoValue = styled.Text`
  font-size: 17px;
  font-weight: bold;
  color: #000;
`;

const InfoHighlight = styled.Text`
  font-size: 15px;
  color: #2D64F4;
  margin-top: 4px;
`;

const JoinButtonLight = styled.TouchableOpacity`
  background-color: #C0EEF2;
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  margin-bottom: 24px;
`;

const JoinButtonLightText = styled.Text`
  color: #176B87;
  font-size: 16px;
  font-weight: bold;
`;

const BottomSection = styled.View`
  background-color: #fff;
  padding: 20px;
`;

const PromotionText = styled.Text`
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  line-height: 26px;
  margin-bottom: 24px;
`;

const MainImage = styled.Image`
  width: 100%;
  height: 200px;
  resize-mode: contain;
  margin-bottom: 32px;
`;

const InfoContainer = styled.View`
  margin-top: 24px;
`;

const InfoItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  padding-vertical: 12px;
  border-bottom-width: 1px;
  border-bottom-color: #eee;
`;

const InfoLabel = styled.Text`
  color: #666;
`;

const StepContainer = styled.View`
  margin-top: 32px;
  margin-bottom: 24px;
`;

const StepTitle = styled.Text`
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
`;

const StepItem = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 16px;
`;

const StepNumber = styled.Text`
  width: 24px;
  height: 24px;
  border-radius: 12px;
  background-color: #007AFF;
  color: #fff;
  text-align: center;
  line-height: 24px;
  margin-right: 12px;
`;

const StepText = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-right: 8px;
`;

const StepDesc = styled.Text`
  font-size: 14px;
  color: #666;
  flex: 1;
`;

const JoinButton = styled.TouchableOpacity`
  background-color: #007AFF;
  padding: 16px;
  border-radius: 8px;
  align-items: center;
`;

const JoinButtonText = styled.Text`
  color: #fff;
  font-weight: bold;
`;

const SavingsJoinScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <SafeAreaView style={{ flex: 1 }}>
          <Content>
            <TitleContainer>
              <BackButton onPress={() => navigation.goBack()}>
                <Ionicons name="chevron-back" size={24} color="black" />
              </BackButton>
              <Title>야금야금</Title>
            </TitleContainer>

            <ScrollView showsVerticalScrollIndicator={false}>
              <TopSection>
                <TagContainer>
                  <Tag>#KBO 야구</Tag>
                  <Tag>#자유적금</Tag>
                  <Tag>#우대금리</Tag>
                </TagContainer>

                <InfoBox>
                  <InfoColumn>
                    <CardIconPlaceholder />
                    <InfoTitle>이자율</InfoTitle>
                    <InfoValue>기본 2.00%</InfoValue>
                    <InfoHighlight>최대 4.00%</InfoHighlight>
                  </InfoColumn>
                  <InfoColumn>
                    <CardIconPlaceholder />
                    <InfoTitle>납입 금액</InfoTitle>
                    <InfoValue>월 70만원 이내</InfoValue>
                  </InfoColumn>
                </InfoBox>

                <JoinButtonLight>
                  <JoinButtonLightText>가입하기</JoinButtonLightText>
                </JoinButtonLight>
              </TopSection>

              <BottomSection>
                <PromotionText>
                  아구 경기 보는 재미와{'\n'}
                  적금의 혜택을 함께해요!
                </PromotionText>

                <MainImage 
                  source={require('../../assets/squirrel.png')} 
                />

                <InfoContainer>
                  <StepTitle>상품 안내</StepTitle>
                  <InfoItem>
                    <InfoLabel>상품명</InfoLabel>
                    <InfoValue>KBO 자유 적금 아금아금</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>계약기간</InfoLabel>
                    <InfoValue>7개월</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>금리</InfoLabel>
                    <InfoValue>기본 2.00% (최대 4.00%)</InfoValue>
                  </InfoItem>
                </InfoContainer>

                <StepContainer>
                  <StepTitle>계좌 개설 절차</StepTitle>
                  <StepItem>
                    <StepNumber>1</StepNumber>
                    <StepText>본인인 인증</StepText>
                    <StepDesc>KBO 자유 적금 등 동의하는 단계</StepDesc>
                  </StepItem>
                  <StepItem>
                    <StepNumber>2</StepNumber>
                    <StepText>정보 입력 단계</StepText>
                    <StepDesc>계좌 정보 입력 단계</StepDesc>
                  </StepItem>
                  <StepItem>
                    <StepNumber>3</StepNumber>
                    <StepText>약관 동의 절차</StepText>
                    <StepDesc>서비스, 상품과 관련된 동의 하는 단계</StepDesc>
                  </StepItem>
                  <StepItem>
                    <StepNumber>4</StepNumber>
                    <StepText>약관 동의 절차</StepText>
                    <StepDesc>금리 정보와 약관 적용 조항을 설명</StepDesc>
                  </StepItem>
                  <StepItem>
                    <StepNumber>5</StepNumber>
                    <StepText>계좌 개설 확인</StepText>
                  </StepItem>
                </StepContainer>

                <JoinButton>
                  <JoinButtonText>가입하기</JoinButtonText>
                </JoinButton>
              </BottomSection>
            </ScrollView>
          </Content>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    maxWidth: 430,
    width: '100%',
    backgroundColor: '#fff',
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    backgroundColor: 'rgba(192, 238, 242, 0.2)',
    width: '100%',
  },
  backButton: {
    alignSelf: 'flex-start',
    padding: 8,
  },
  title: {
    fontWeight: 'bold',
    flex: 1,
    textAlign: 'center',
    marginRight: 32,
    color: '#000',
  },
  tagContainer: {
    flexDirection: 'row',
    marginBottom: 32,
    justifyContent: 'center',
    gap: 12,
    paddingVertical: 16,
  },
  tag: {
    color: '#666',
    fontSize: 15,
    fontWeight: '500',
  },
  topSection: {
    backgroundColor: 'rgba(192, 238, 242, 0.2)',
    width: '100%',
    paddingHorizontal: 20,
    marginTop: -16,  // titleContainer의 marginBottom 상쇄
  },
  bottomSection: {
    backgroundColor: '#fff',
  },
  infoBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
    gap: 12,
  },
  infoColumn: {
    flex: 1,
    alignItems: 'center',
  },
  infoTitle: {
    fontSize: 15,
    color: '#666',
    marginBottom: 8,
  },
  infoValue: {
    fontSize: 17,
    fontWeight: 'bold',
    color: '#000',
  },
  infoHighlight: {
    fontSize: 15,
    color: '#2D64F4',
    marginTop: 4,
  },
  promotionText: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    lineHeight: 26,
    marginBottom: 24,
  },
  mainImage: {
    width: '100%',
    height: 200,
    resizeMode: 'contain',
    marginBottom: 32,
  },
  infoContainer: {
    marginTop: 24,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  infoLabel: {
    color: '#666',
  },
  stepContainer: {
    marginTop: 32,
    marginBottom: 24,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  stepNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#007AFF',
    color: '#fff',
    textAlign: 'center',
    lineHeight: 24,
    marginRight: 12,
  },
  stepText: {
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 8,
  },
  stepDesc: {
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  joinButtonLight: {
    backgroundColor: '#C0EEF2',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 24,
    marginHorizontal: 0,
  },
  joinButtonLightText: {
    color: '#176B87',
    fontSize: 16,
    fontWeight: 'bold',
  },
  joinButton: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  joinButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  cardIconPlaceholder: {
    width: 48,
    height: 48,
    marginBottom: 12,
    backgroundColor: '#fff',
    borderRadius: 24,
  },
});

export default SavingsJoinScreen; 