import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, SafeAreaView, Platform, useWindowDimensions, ScrollView, Pressable, Animated, NativeSyntheticEvent, NativeScrollEvent } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AppWrapper, MobileContainer, getAdjustedWidth } from '../constants/layout';
import styled from 'styled-components/native';
import TeamSelectModal from '../components/TeamSelectModal';
import { BlurView } from 'expo-blur';

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
  padding-left: 16px;
  margin-left: 4px;
`;

const Title = styled.Text`
  font-weight: bold;
  flex: 1;
  text-align: center;
  margin-right: 48px;
  color: #000;
  font-size: 20px;
`;

const TagContainer = styled.View`
  flex-direction: row;
  margin-bottom: 32px;
  justify-content: center;
  gap: 12px;
  padding-vertical: 16px;
  margin-top: 16px;
`;

const Tag = styled.Text`
  color: #176B87;
  font-size: 15px;
  font-weight: 500;
  background-color: rgba(192, 238, 242, 0.3);
  padding: 6px 12px;
  border-radius: 16px;
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
  margin-bottom: 40px;
  gap: 12px;
`;

const InfoColumn = styled.View`
  flex: 1;
  align-items: center;
`;

const IconContainer = styled.View`
  width: 64px;
  height: 64px;
  background-color: #fff;
  border-radius: 32px;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  elevation: 3;
  shadow-color: #000;
  shadow-offset: 0px 2px;
  shadow-opacity: 0.1;
  shadow-radius: 4px;
`;

const IconImage = styled.Image`
  width: 42px;
  height: 42px;
`;

const InfoTitle = styled.Text`
  font-size: 18px;
  font-weight: 700;
  color: #000000;
  margin-bottom: 4px;
`;

const TopInfoValue = styled.Text`
  font-size: 14px;
  color: #222222;
  font-weight: 500;
  line-height: 20px;
  text-align: center;
`;

const TopInfoHighlight = styled.Text`
  font-size: 14px;
  color: #2D64F4;
  margin-top: 2px;
`;

const InfoItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  padding-vertical: 12px;
  border-bottom-width: 0.5px;
  border-bottom-color: rgba(0, 0, 0, 0.1);
  align-items: center;
`;

const InfoLabel = styled.Text`
  font-size: 14px;
  color: #999999;
  font-weight: 600;
  line-height: 20px;
  width: 70px;
`;

const InfoValue = styled.Text`
  flex: 1;
  font-size: 15px;
  color: #1B1D1F;
  font-weight: 600;
  line-height: 22px;
  text-align: right;
  margin-left: 16px;
`;

const InfoHighlight = styled.Text`
  font-size: 14px;
  color: #2D64F4;
  margin-top: 3px;
`;

const JoinButtonLight = styled.TouchableOpacity`
  background-color: #C0EEF2;
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  margin-bottom: 32px;
  width: 100%;
`;

const JoinButtonLightText = styled.Text`
  color: #176B87;
  font-size: 18px;
  font-weight: 900;
`;

const BottomSection = styled.View`
  background-color: #fff;
  padding: 20px;
  padding-bottom: 16px;
`;

const PromotionContainer = styled.View`
  margin-bottom: 8px;
  margin-top: 24px;
`;

const PromotionText = styled.Text`
  font-size: 24px;
  font-weight: bold;
  text-align: left;
  line-height: 32px;
  margin-bottom: 8px;
`;

const HighlightText = styled(PromotionText)`
  color: #176B87;
  font-weight: 900;
`;

const SubPromotionText = styled.Text`
  font-size: 14px;
  color: #666;
  line-height: 20px;
  margin-bottom: 16px;
`;

const MainImage = styled.Image`
  width: 240px;
  height: 240px;
  resize-mode: contain;
  align-self: flex-end;
  margin-right: -20px;
  margin-top: -30px;
  margin-bottom: 12px;
`;

const SectionDivider = styled.View`
  width: 100vw;
  height: 8px;
  background-color: #F8F9FA;
  margin-horizontal: -20px;
`;

const InfoContainer = styled.View`
  margin-top: 4px;
  background-color: #FFFFFF;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  padding-top: 32px;
`;

const StepContainer = styled.View`
  margin-top: 32px;
  padding-bottom: 16px;
`;

const StepTitle = styled.Text`
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 28px;
  color: #1B1D1F;
  letter-spacing: -0.4px;
`;

const StepItem = styled(Animated.View)`
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-right: 0;
  width: 100%;
`;

const StepNumber = styled.View`
  width: 28px;
  height: 28px;
  border-radius: 14px;
  background-color: rgba(23, 107, 135, 0.1);
  justify-content: center;
  align-items: center;
  margin-right: 16px;
`;

const StepNumberText = styled.Text`
  color: #176B87;
  font-size: 15px;
  font-weight: 700;
`;

const StepContent = styled.View`
  flex: 1;
  padding-right: 0;
`;

const StepText = styled.Text`
  font-size: 17px;
  font-weight: 700;
  color: #1B1D1F;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
`;

const StepDesc = styled.Text`
  font-size: 15px;
  color: #64666B;
  line-height: 22px;
  letter-spacing: -0.2px;
  flex-shrink: 1;
  padding-right: 0;
`;

const JoinButton = styled.TouchableOpacity`
  background-color: #007AFF;
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  margin-top: 0px;
  margin-bottom: 16px;
  width: 100%;
`;

const JoinButtonText = styled.Text`
  color: #fff;
  font-size: 18px;
  font-weight: 900;
`;

const stepTexts = [
  {
    title: '팀 선택',
    desc: '응원하고 싶은 구단을 선택하는 단계'
  },
  {
    title: '최애 선수 선택',
    desc: '선택한 구단의 선수를 선택하는 단계'
  },
  {
    title: '적금 목표 선택',
    desc: '시즌 동안의 적금 목표를 설정하는 단계'
  },
  {
    title: '적금 규칙 설정',
    desc: '경기 결과에 따른 적립 규칙을 설정하는 단계'
  },
  {
    title: '약관 동의 및 출금 계좌 선택',
    desc: '필수 약관 동의와 출금 계좌를 설정하는 단계'
  },
  {
    title: '가입 완료',
    desc: '설정한 내용을 확인하고 가입 완료'
  }
];

const BlurContainer = styled(BlurView)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
`;

const SavingsJoinScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const [isStepVisible, setIsStepVisible] = React.useState(false);
  const stepAnimations = React.useRef(stepTexts.map(() => new Animated.Value(0))).current;
  const [isModalVisible, setIsModalVisible] = useState(false);

  const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
    const scrollY = event.nativeEvent.contentOffset.y;
    const layoutHeight = event.nativeEvent.layoutMeasurement.height;
    const contentHeight = event.nativeEvent.contentSize.height;
    
    // 스크롤이 전체 컨텐츠의 40% 정도 진행되었을 때 애니메이션 시작
    if (scrollY > contentHeight * 0.4 && !isStepVisible) {
      setIsStepVisible(true);
      Animated.stagger(100, stepAnimations.map(animation =>
        Animated.spring(animation, {
          toValue: 1,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        })
      )).start();
    }
  };

  const handleJoinPress = () => {
    setIsModalVisible(true);
  };

  const handleTeamSelect = (teamId: string) => {
    console.log('Selected team:', teamId);
    setIsModalVisible(false);
    // TODO: 팀 선택 후 처리 로직
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <SafeAreaView style={{ flex: 1 }}>
          <Content>
            {isModalVisible && (
              <BlurContainer
                intensity={10}
                tint="light"
              />
            )}
            <TitleContainer>
              <BackButton onPress={() => navigation.goBack()}>
                <Ionicons name="chevron-back" size={24} color="black" />
              </BackButton>
              <Title>야금야금</Title>
            </TitleContainer>

            <ScrollView 
              showsVerticalScrollIndicator={false}
              onScroll={handleScroll}
              scrollEventThrottle={16}
            >
              <TopSection>
                <TagContainer>
                  <Tag>#KBO 야구</Tag>
                  <Tag>#자유적금</Tag>
                  <Tag>#우대금리</Tag>
                </TagContainer>

                <InfoBox>
                  <InfoColumn>
                    <IconContainer>
                      <IconImage source={require('../../assets/rate.png')} />
                    </IconContainer>
                    <InfoTitle>이자율</InfoTitle>
                    <TopInfoValue>기본 2.50%</TopInfoValue>
                    <TopInfoHighlight>최대 3.80%</TopInfoHighlight>
                  </InfoColumn>
                  <InfoColumn>
                    <IconContainer>
                      <IconImage source={require('../../assets/saving.png')} />
                    </IconContainer>
                    <InfoTitle>납입 금액</InfoTitle>
                    <TopInfoValue>월 50만원 이내</TopInfoValue>
                  </InfoColumn>
                </InfoBox>

                <JoinButtonLight onPress={handleJoinPress}>
                  <JoinButtonLightText>가입하기</JoinButtonLightText>
                </JoinButtonLight>
              </TopSection>

              <BottomSection>
                <PromotionContainer>
                  <PromotionText>
                    <HighlightText>야구 경기</HighlightText>
                    <PromotionText> 보는 재미와{'\n'}</PromotionText>
                    <HighlightText>적금의 혜택</HighlightText>
                    <PromotionText>을 한번에 !</PromotionText>
                  </PromotionText>
                </PromotionContainer>
                <SubPromotionText>
                  팀과 선수 경기 기록으로 자동 적금{'\n'}
                  KBO 시즌 동안 모으고 우대금리 혜택까지
                </SubPromotionText>
                <MainImage 
                  source={require('../../assets/squirrel.png')}
                />
                <SectionDivider />
                <InfoContainer>
                  <InfoTitle>상품 안내</InfoTitle>
                  <InfoItem>
                    <InfoLabel>상품명</InfoLabel>
                    <InfoValue>KBO 자유 적금 '야금야금'</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>계약기간</InfoLabel>
                    <InfoValue>7개월</InfoValue>
                  </InfoItem>
                  <InfoItem>
                    <InfoLabel>금리</InfoLabel>
                    <InfoValue>기본 2.50% (최대 3.80%)</InfoValue>
                  </InfoItem>
                </InfoContainer>

                <StepContainer>
                  <StepTitle>계좌 개설 절차</StepTitle>
                  {stepTexts.map((step, index) => (
                    <StepItem
                      key={index}
                      style={{
                        opacity: stepAnimations[index],
                        transform: [{
                          translateX: stepAnimations[index].interpolate({
                            inputRange: [0, 1],
                            outputRange: [20, 0],
                          })
                        }]
                      }}
                    >
                      <StepNumber>
                        <StepNumberText>{index + 1}</StepNumberText>
                      </StepNumber>
                      <StepContent>
                        <StepText>{step.title}</StepText>
                        <StepDesc>{step.desc}</StepDesc>
                      </StepContent>
                    </StepItem>
                  ))}
                </StepContainer>

                <JoinButton onPress={handleJoinPress}>
                  <JoinButtonText>가입하기</JoinButtonText>
                </JoinButton>
              </BottomSection>
            </ScrollView>

            <TeamSelectModal
              visible={isModalVisible}
              onClose={() => setIsModalVisible(false)}
              onSelectTeam={handleTeamSelect}
              width={width}
            />
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
    marginRight: 48,
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
    marginBottom: 32,
  },
  joinButtonLightText: {
    color: '#176B87',
    fontSize: 18,
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
    fontSize: 18,
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