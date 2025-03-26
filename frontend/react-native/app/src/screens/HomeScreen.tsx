import React, { useState, useEffect, useRef } from 'react';
import { useWindowDimensions, SafeAreaView, ScrollView, Platform, Pressable, View, Text, Animated, Image, Alert, ActivityIndicator, TouchableOpacity, Dimensions } from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import styled from 'styled-components/native';
import { LinearGradient } from 'expo-linear-gradient';
import {
  AppWrapper,
  MobileContainer,
  getAdjustedWidth,
  StyledProps,
  BASE_MOBILE_WIDTH
} from '../constants/layout';
import * as Haptics from 'expo-haptics';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useStore } from '../store/useStore';
import * as Clipboard from 'expo-clipboard';
import Toast from 'react-native-root-toast';
import { useAccountStore } from '../store/useStore';

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

const Container = styled.View<StyledProps>`
  flex: 1;
  width: 100%;
  padding: ${({ width }) => {
    const baseWidth = Platform.OS === 'web' ? BASE_MOBILE_WIDTH : width;
    return baseWidth * 0.045;
  }}px;
`;

const Header = styled.View<StyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.width * 0.04}px;
`;

const HeaderTitle = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.06}px;
  font-weight: bold;
  color: #333;
`;

const IconContainer = styled.View`
  flex-direction: row;
  align-items: center;
`;

const IconButton = styled.TouchableOpacity<StyledProps>`
  padding: ${({ width }) => width * 0.02}px;
  margin-left: ${({ width }) => width * 0.02}px;
`;

const ServiceCardWrapper = styled.TouchableOpacity<StyledProps>`
  background-color: #F0F2FF;
  border-radius: ${({ width }) => width * 0.025}px;
  padding: ${props => props.width * 0.045}px;
  margin-bottom: ${props => props.width * 0.025}px;
  width: 100%;
  ${Platform.select({
    ios: {
      shadowColor: '#2D5BFF',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.08,
      shadowRadius: 4,
    },
    android: {
      elevation: 2,
    },
    web: {
      boxShadow: '0 2px 4px rgba(45, 91, 255, 0.08)'
    }
  })}
`;

const webStyles = Platform.OS === 'web' ? {
  serviceCard: {
    transition: 'all 0.2s ease-in-out',
    ':hover': {
      transform: 'scale(1.01)',
      boxShadow: '0 4px 12px rgba(107, 119, 248, 0.15)',
      cursor: 'pointer'
    }
  },
  startButton: {
    transition: 'all 0.2s ease-in-out',
    ':hover': {
      transform: 'scale(1.02)',
      opacity: 0.95,
      cursor: 'pointer'
    }
  },
  iconButton: {
    transition: 'all 0.2s ease-in-out',
    ':hover': {
      transform: 'scale(1.1)',
      opacity: 0.8,
      cursor: 'pointer'
    }
  }
} : {};

const ServiceTitleContainer = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
`;

const ContentContainer = styled.View`
  flex-direction: row;
  align-items: center;
  gap: 8px;
  flex: 1;
`;

const ServiceTextContainer = styled.View<StyledProps>`
  flex: 1;
  padding-right: 0;
`;

const ServiceIcon = styled.Image`
  width: 40px;
  height: 40px;
  margin-right: 4px;
`;

const ServiceTitle = styled.Text<StyledProps>`
  font-size: ${props => props.width * 0.045}px;
  line-height: ${props => props.width * 0.062}px;
  font-weight: bold;
  letter-spacing: -0.3px;
  color: #333;
`;

const ColoredText = styled.Text`
  color: #2D5BFF;
  font-weight: bold;
`;

const BlackText = styled.Text`
  color: black;
  font-weight: bold;
`;

const LightText = styled.Text`
  color: #999999;
  font-weight: bold;
`;

const ServiceDescription = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.038}px;
  line-height: ${({ width }) => width * 0.052}px;
  color: #222222;
  letter-spacing: -0.3px;
`;

const StartButton = styled.TouchableOpacity<StyledProps>`
  background-color: ${({ theme }) => theme.colors.primary};
  padding: ${({ width }) => width * 0.03}px;
  border-radius: ${({ width }) => width * 0.02}px;
  align-items: center;
  margin-top: ${({ width }) => width * 0.025}px;
`;

const ButtonText = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.04}px;
  font-weight: bold;
`;

const RecommendSection = styled.View<StyledProps>`
  margin-top: ${({ width }) => width * 0.0}px;
`;

const SectionTitle = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.046}px;
  font-weight: 900;
  color: #222222;
  margin-bottom: ${({ width }) => width * 0.008}px;
`;

const AuthCard = styled.View<StyledProps>`
  background-color: white;
  border-radius: ${({ width }) => width * 0.025}px;
  padding: ${props => props.width * 0.045}px;
  margin-bottom: ${props => props.width * 0.05}px;
  width: 100%;
  min-height: ${props => props.width * 0.52}px;
  ${Platform.select({
  ios: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
  },
  android: {
    elevation: 3,
  },
  web: {
    boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.08)'
  }
})}
`;

const AuthCardContent = styled.View`
  flex: 1;
  justify-content: space-between;
`;

const AuthCardHeader = styled.View<StyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-top: ${({ width }) => width * -0.02}px;
`;

const AuthCardBody = styled.View`
  flex: 1;
`;

const AuthCardText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.0425}px;
  font-weight: bold;
  margin-bottom: 8px;
  line-height: ${({ width }) => width * 0.06}px;
`;

const AuthCardImage = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.35}px;
  height: ${({ width }) => width * 0.35}px;
  margin-left: ${({ width }) => width * 0.02}px;
  padding-top: ${({ width }) => width * 0.01}px;
`;

const AccountInfo = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 8px;
`;

const AccountRow = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 8px;
`;

const AccountNumberContainer = styled.View`
  flex: 1;
`;

const AccountNumberRow = styled.View`
  flex-direction: row;
  align-items: center;
`;

const AccountTypeText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.038}px;
  color: #000;
  line-height: ${({ width }) => width * 0.052}px;
  font-weight: 600;
`;

const AccountNumberText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.038}px;
  color: #666;
  line-height: ${({ width }) => width * 0.052}px;
`;

const CopyButton = styled.TouchableOpacity`
  padding-left: 4px;
  align-items: center;
  justify-content: center;
`;

const BalanceRow = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
`;

const AccountLeftSection = styled.View`
  flex-direction: row;
  align-items: center;
`;

const AccountRightSection = styled.View`
  flex-direction: row;
  align-items: center;
  gap: 8px;
`;

const AccountIcon = styled.Image`
  width: 24px;
  height: 24px;
  margin-right: 8px;
`;

const BalanceContainer = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 0px;
`;

const Balance = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.072}px;
  font-weight: 700;
  color: #000;
  margin: 0;
`;

const ButtonContainer = styled.View`
  flex-direction: row;
  gap: 12px;
  margin-top: 16px;
`;

const ActionButton = styled.TouchableOpacity<StyledProps>`
  flex: 1;
  background-color: #F0F2FF;
  padding: ${({ width }) => width * 0.035}px;
  border-radius: ${({ width }) => width * 0.02}px;
  align-items: center;
`;

const ButtonLabel = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.036}px;
  color: #2D5BFF;
  font-weight: 600;
`;

const HomeScreen = () => {
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const iconSize = width * 0.06;
  const navigation = useNavigation<NavigationProp>();
  const { isLoggedIn } = useStore();
  const { accountInfo, isLoading, error, fetchAccountInfo } = useAccountStore();

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideUpAnim = useRef(new Animated.Value(50)).current;
  const firstCardScale = useRef(new Animated.Value(1)).current;
  const recommendCardScale = useRef(new Animated.Value(1)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (isLoggedIn) {
      fetchAccountInfo();
    }
  }, [isLoggedIn, fetchAccountInfo]);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true
      }),
      Animated.timing(slideUpAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true
      })
    ]).start();
  }, [fadeAnim, slideUpAnim]);

  const onFirstCardPress = () => {
    Animated.sequence([
      Animated.timing(firstCardScale, {
        toValue: 0.98,
        duration: 150,
        useNativeDriver: true
      }),
      Animated.timing(firstCardScale, {
        toValue: 1,
        duration: 150,
        useNativeDriver: true
      })
    ]).start();
  };

  const onRecommendCardPress = () => {
    Animated.sequence([
      Animated.timing(recommendCardScale, {
        toValue: 0.97,
        duration: 100,
        useNativeDriver: true
      }),
      Animated.timing(recommendCardScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true
      })
    ]).start();
  };

  const onStartButtonPress = () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    navigation.navigate('Login');
  };

  const AnimatedServiceCard = Animated.createAnimatedComponent(ServiceCardWrapper);
  const AnimatedStartButton = Animated.createAnimatedComponent(StartButton);
  const AnimatedScrollView = Animated.createAnimatedComponent(ScrollView);

  // 계좌 정보 렌더링 함수
  const renderAccountSection = () => {
    return (
      <AnimatedServiceCard
        width={width}
        style={[
          { 
            backgroundColor: '#F0F2FF',
            ...Platform.select({
              ios: {
                shadowColor: '#2D5BFF',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.08,
                shadowRadius: 4,
              },
              android: {
                elevation: 2,
              },
              web: {
                boxShadow: '0 2px 4px rgba(45, 91, 255, 0.08)'
              }
            })
          },
          { transform: [{ scale: firstCardScale }] }
        ]}
        onPress={onFirstCardPress}
        activeOpacity={1}
      >
        <ServiceTitleContainer>
          <ContentContainer>
            <ServiceIcon
              source={require('../../assets/baseball.png')}
              width={width}
              resizeMode="contain"
            />
            <ServiceTextContainer width={width}>
              <ServiceTitle width={width}>
                <Text style={{ fontSize: width * 0.034 }}>
                  <BlackText>{accountInfo?.user_name || '김싸피'}</BlackText>
                  <LightText>님을 위한 맞춤 서비스,</LightText>
                </Text>
                {'\n'}
                <ColoredText>야금야금</ColoredText>
                <BlackText>적금</BlackText>
              </ServiceTitle>
            </ServiceTextContainer>
          </ContentContainer>
          <MaterialIcons name="chevron-right" size={24} color="rgba(0, 0, 0, 0.25)" />
        </ServiceTitleContainer>
      </AnimatedServiceCard>
    );
  };

  // 두 번째 섹션 렌더링 함수
  const renderSecondSection = () => {
    return (
      <AuthCard width={width}>
        <AuthCardContent>
          <AuthCardBody>
            {isLoggedIn ? (
              <>
                <AccountRow>
                  <AccountIcon source={require('../../assets/shinhan-icon.png')} />
                  <AccountNumberContainer>
                    <AccountTypeText width={width}>입출금 통장(자유예금)</AccountTypeText>
                    <AccountNumberRow>
                      <AccountNumberText width={width}>{accountInfo?.source_account.account_num || '111-222-333333'}</AccountNumberText>
                      <CopyButton onPress={async () => {
                        await Clipboard.setStringAsync(accountInfo?.source_account.account_num || '111-222-333333');
                        Toast.show('✓ 계좌번호가 복사되었습니다', {
                          duration: Toast.durations.SHORT,
                          position: Toast.positions.BOTTOM,
                          shadow: true,
                          animation: true,
                          hideOnPress: true,
                          delay: 0,
                          backgroundColor: 'rgba(45, 45, 45, 0.95)',
                          textColor: '#ffffff',
                          opacity: 0.95,
                          containerStyle: {
                            borderRadius: 16,
                            paddingHorizontal: 20,
                            paddingVertical: 14,
                            marginBottom: 40,
                            flexDirection: 'row',
                            alignItems: 'center',
                            gap: 8,
                            ...Platform.select({
                              ios: {
                                shadowColor: '#000',
                                shadowOffset: { width: 0, height: 4 },
                                shadowOpacity: 0.15,
                                shadowRadius: 8,
                              },
                              android: {
                                elevation: 6,
                              },
                              web: {
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                              }
                            })
                          }
                        });
                      }}>
                        <Ionicons name="copy-outline" size={16} color="rgba(0, 0, 0, 0.35)" />
                      </CopyButton>
                    </AccountNumberRow>
                  </AccountNumberContainer>
                </AccountRow>
                <BalanceRow>
                  <Balance width={width}>{accountInfo?.source_account.total_amount.toLocaleString()}원</Balance>
                </BalanceRow>
              </>
            ) : (
              <AuthCardHeader width={width}>
                <View style={{ flex: 1 }}>
                  <AuthCardText width={width}>
                    간편하게 <Text style={{ color: '#2D5BFF' }}>본인인증</Text>하고{'\n'}
                    서비스를 이용해보세요.
                  </AuthCardText>
                </View>
                <AuthCardImage
                  source={require('../../assets/verification.png')}
                  width={width}
                  resizeMode="contain"
                />
              </AuthCardHeader>
            )}
          </AuthCardBody>
          {isLoggedIn ? (
            <ButtonContainer>
              <ActionButton width={width}>
                <ButtonLabel width={width}>이체</ButtonLabel>
              </ActionButton>
              <ActionButton width={width}>
                <ButtonLabel width={width}>간편앱출금</ButtonLabel>
              </ActionButton>
            </ButtonContainer>
          ) : (
            <AnimatedStartButton
              width={width}
              onPress={onStartButtonPress}
              style={{ transform: [{ scale: buttonScale }] }}
            >
              <ButtonText width={width}>시작하기</ButtonText>
            </AnimatedStartButton>
          )}
        </AuthCardContent>
      </AuthCard>
    );
  };

  return (
    <>
      <AppWrapper>
        <MobileContainer width={width}>
          <LinearGradient
            colors={['#FFFFFF', '#E6EFFE']}
            locations={[0.19, 1.0]}
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              top: 0,
              bottom: 0,
            }}
          />
          <SafeAreaView style={{ flex: 1 }}>
            <AnimatedScrollView
              style={[
                { flex: 1 },
                {
                  opacity: fadeAnim,
                  transform: [{ translateY: slideUpAnim }]
                }
              ]}
              contentContainerStyle={{
                flexGrow: 1,
                width: '100%'
              }}
            >
              <Container width={width}>
                <Header width={width}>
                  <HeaderTitle width={width}>홈</HeaderTitle>
                  <IconContainer>
                    <IconButton width={width}>
                      <MaterialIcons name="chat-bubble-outline" size={iconSize} color="black" />
                    </IconButton>
                    <IconButton width={width}>
                      <MaterialIcons name="mic-none" size={iconSize} color="black" />
                    </IconButton>
                    <IconButton width={width} onPress={onStartButtonPress}>
                      <MaterialIcons
                        name={isLoggedIn ? "logout" : "login"}
                        size={iconSize}
                        color="black"
                      />
                    </IconButton>
                  </IconContainer>
                </Header>

                {renderAccountSection()}
                {renderSecondSection()}

                <RecommendSection width={width}>
                  <AnimatedServiceCard
                    width={width}
                    style={[
                      { backgroundColor: '#FFFFFF' },
                      { transform: [{ scale: recommendCardScale }] }
                    ]}
                    onPress={onRecommendCardPress}
                    activeOpacity={1}
                  >
                    <SectionTitle width={width} style={{ marginBottom: width * 0.005 }}>추천</SectionTitle>
                    <ServiceTitleContainer>
                      <ServiceTextContainer width={width}>
                        <ServiceTitle width={width} style={{ marginBottom: 4 }}>
                          <ColoredText style={{ fontWeight: '700' }}>야금야금</ColoredText>
                        </ServiceTitle>
                        <ServiceDescription width={width}>
                          지루했던 금융에
                          {'\n'}
                          야구의 재미를 더하다!
                        </ServiceDescription>
                      </ServiceTextContainer>
                      <ServiceIcon
                        source={require('../../assets/recommend.png')}
                        resizeMode="contain"
                        style={{
                          width: 170,
                          height: 170,
                          marginLeft: 'auto',
                          marginRight: -10
                        }}
                      />
                    </ServiceTitleContainer>
                  </AnimatedServiceCard>
                </RecommendSection>
              </Container>
            </AnimatedScrollView>
          </SafeAreaView>
        </MobileContainer>
      </AppWrapper>
    </>
  );
};

export default HomeScreen; 