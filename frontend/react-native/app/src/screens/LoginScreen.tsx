import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Animated, Platform, useWindowDimensions } from 'react-native';
import styled from 'styled-components/native';
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { 
  AppWrapper, 
  MobileContainer, 
  getAdjustedWidth,
  StyledProps 
} from '../constants/layout';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList, 'Login'>;

const Container = styled.View<StyledProps>`
  flex: 1;
  width: 100%;
  padding: ${({ width }) => width * 0.045}px;
`;

const Header = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.04}px;
`;

const BackButton = styled.TouchableOpacity<StyledProps>`
  padding: ${({ width }) => width * 0.01}px;
`;

const ContentContainer = styled.View`
  flex: 1;
  justify-content: center;
`;

const LoginCard = styled.View<StyledProps>`
  background-color: white;
  border-radius: ${({ width }) => width * 0.025}px;
  padding: ${props => props.width * 0.045}px;
  width: 100%;
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

const CharacterImage = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.4}px;
  height: ${({ width }) => width * 0.4}px;
  align-self: center;
  margin-bottom: ${({ width }) => width * 0.03}px;
`;

const Title = styled.Text<StyledProps>`
  font-size: ${props => props.width * 0.055}px;
  font-weight: bold;
  margin-bottom: ${props => props.width * 0.035}px;
  text-align: center;
`;

const InputContainer = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  border-radius: ${({ width }) => width * 0.015}px;
  background-color: #F5F6FF;
  padding: ${({ width }) => width * 0.035}px;
  margin-bottom: ${({ width }) => width * 0.02}px;
`;

const Input = styled.TextInput<StyledProps>`
  flex: 1;
  font-size: ${({ width }) => width * 0.04}px;
  margin-left: ${({ width }) => width * 0.02}px;
  color: #333;
  outline: none;
  &::placeholder {
    color: #999;
  }
`;

const LoginButton = styled.TouchableOpacity<StyledProps>`
  background-color: #2D5BFF;
  padding: ${({ width }) => width * 0.035}px;
  border-radius: ${({ width }) => width * 0.015}px;
  align-items: center;
  margin-top: ${({ width }) => width * 0.03}px;
`;

const ButtonText = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.04}px;
  font-weight: bold;
`;

const ForgotPassword = styled.TouchableOpacity`
  align-self: center;
  margin-top: 16px;
`;

const ForgotPasswordText = styled.Text<StyledProps>`
  color: #666;
  font-size: ${({ width }) => width * 0.035}px;
`;

const LoginScreen = () => {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [idFocused, setIdFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const navigation = useNavigation<NavigationProp>();

  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const iconSize = width * 0.055;

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
        <Container width={width}>
          <Header width={width}>
            <BackButton 
              width={width}
              onPress={() => navigation.goBack()}
            >
              <MaterialIcons 
                name="arrow-back-ios" 
                size={iconSize} 
                color="#333" 
              />
            </BackButton>
          </Header>
          <ContentContainer>
            <LoginCard width={width}>
              <CharacterImage 
                source={require('../../assets/verification.png')} 
                width={width}
                resizeMode="contain"
              />
              <Title width={width}>로그인</Title>
              
              <InputContainer width={width}>
                <MaterialIcons name="person-outline" size={iconSize} color="#666" />
                <Input
                  width={width}
                  placeholder={idFocused ? "" : "아이디를 입력해주세요"}
                  value={id}
                  onChangeText={setId}
                  autoCapitalize="none"
                  onFocus={() => setIdFocused(true)}
                  onBlur={() => setIdFocused(false)}
                />
              </InputContainer>

              <InputContainer width={width}>
                <MaterialIcons name="lock-outline" size={iconSize} color="#666" />
                <Input
                  width={width}
                  placeholder={passwordFocused ? "" : "비밀번호를 입력해주세요"}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  onFocus={() => setPasswordFocused(true)}
                  onBlur={() => setPasswordFocused(false)}
                />
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                  <MaterialIcons 
                    name={showPassword ? "visibility" : "visibility-off"} 
                    size={iconSize} 
                    color="#666" 
                  />
                </TouchableOpacity>
              </InputContainer>

              <LoginButton width={width}>
                <ButtonText width={width}>로그인</ButtonText>
              </LoginButton>

              <ForgotPassword>
                <ForgotPasswordText width={width}>
                  아이디/비밀번호 찾기
                </ForgotPasswordText>
              </ForgotPassword>
            </LoginCard>
          </ContentContainer>
        </Container>
      </MobileContainer>
    </AppWrapper>
  );
};

export default LoginScreen; 