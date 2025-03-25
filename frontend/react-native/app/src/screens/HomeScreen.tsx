import { useWindowDimensions, SafeAreaView, ScrollView, Platform, Pressable, View, Text, Animated } from 'react-native';
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
import { useRef, useEffect } from 'react';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

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
  background-color: white;
  border-radius: ${({ width }) => width * 0.025}px;
  padding: ${props => props.width * 0.045}px;
  margin-bottom: ${props => props.width * 0.025}px;
  width: 100%;
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

const HomeScreen = () => {
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const iconSize = width * 0.06;
  const navigation = useNavigation<NavigationProp>();

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideUpAnim = useRef(new Animated.Value(50)).current;
  const firstCardScale = useRef(new Animated.Value(1)).current;
  const recommendCardScale = useRef(new Animated.Value(1)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

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
  }, []);

  const onFirstCardPress = () => {
    Animated.sequence([
      Animated.timing(firstCardScale, {
        toValue: 0.97,
        duration: 100,
        useNativeDriver: true
      }),
      Animated.timing(firstCardScale, {
        toValue: 1,
        duration: 100,
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
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    Animated.sequence([
      Animated.timing(buttonScale, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true
      }),
      Animated.timing(buttonScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true
      })
    ]).start();
  };

  const AnimatedServiceCard = Animated.createAnimatedComponent(ServiceCardWrapper);
  const AnimatedStartButton = Animated.createAnimatedComponent(StartButton);
  const AnimatedScrollView = Animated.createAnimatedComponent(ScrollView);

  return (
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
                  <IconButton width={width}>
                    <MaterialIcons name="person-outline" size={iconSize} color="black" />
                  </IconButton>
                </IconContainer>
              </Header>

              <AnimatedServiceCard 
                width={width} 
                style={[
                  { backgroundColor: '#F5F6FF' },
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
                        <LightText>나에게 딱 맞는 서비스,</LightText>
                        {'\n'}
                        <ColoredText>야금야금</ColoredText>
                        <BlackText>적금</BlackText>
                      </ServiceTitle>
                    </ServiceTextContainer>
                  </ContentContainer>
                  <MaterialIcons name="chevron-right" size={24} color="#999999" />
                </ServiceTitleContainer>
              </AnimatedServiceCard>

              <View 
                style={{ 
                  backgroundColor: 'white',
                  borderRadius: width * 0.025,
                  padding: width * 0.045,
                  marginBottom: width * 0.025,
                  width: '100%',
                  ...Platform.select({
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
                  })
                }}
              >
                <ServiceTitleContainer>
                  <ServiceTextContainer width={width} style={{ flex: 1.2 }}>
                    <ServiceTitle width={width}>
                      간편하게 <ColoredText>본인인증</ColoredText>하고
                      {'\n'}
                      서비스를 이용해보세요.
                    </ServiceTitle>
                  </ServiceTextContainer>
                  <ServiceIcon 
                    source={require('../../assets/verification.png')} 
                    resizeMode="contain"
                    style={{ 
                      width: 120, 
                      height: 120,
                      marginLeft: -20,
                      marginRight: -15
                    }}
                  />
                </ServiceTitleContainer>
                <AnimatedStartButton 
                  width={width}
                  onPress={() => {
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                    navigation.navigate('Login');
                  }}
                  style={{ transform: [{ scale: buttonScale }] }}
                >
                  <ButtonText width={width}>시작하기</ButtonText>
                </AnimatedStartButton>
              </View>

              <RecommendSection width={width}>
                <AnimatedServiceCard 
                  width={width}
                  style={{ transform: [{ scale: recommendCardScale }] }}
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
  );
};

export default HomeScreen; 