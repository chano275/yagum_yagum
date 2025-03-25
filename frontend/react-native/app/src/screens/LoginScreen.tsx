import React, { useState, useRef } from 'react';
import { View, TextInput, TouchableOpacity, Platform, useWindowDimensions, Alert, ActivityIndicator, TextInputProps, StyleSheet, Image, Text } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { AppWrapper, MobileContainer, getAdjustedWidth, StyledProps } from '../constants/layout';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import axios from 'axios';
import { useAppStore } from '../store/useStore';
import { AppState } from '../store/useStore';

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList, 'Login'>;

const LoginScreen = () => {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [idFocused, setIdFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({
    id: '',
    password: ''
  });

  const navigation = useNavigation<NavigationProp>();
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const iconSize = width * 0.055;
  const passwordInputRef = useRef<TextInput>(null);
  const setAuth = useAppStore((state: AppState) => state.setAuth);

  const validateInputs = () => {
    const newErrors = {
      id: '',
      password: ''
    };

    if (!id.trim()) newErrors.id = '아이디를 입력해주세요';
    if (!password.trim()) newErrors.password = '비밀번호를 입력해주세요';

    setErrors(newErrors);
    return !newErrors.id && !newErrors.password;
  };

  const handleLogin = async () => {
    if (!validateInputs()) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', id);
      formData.append('password', password);

      const response = await axios.post(
        'http://localhost:8000/api/v1/auth/login',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (response.status === 200) {
        const { access_token, user } = response.data;
        setAuth(access_token, user);
        navigation.navigate('Home');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          Alert.alert('로그인 실패', '이메일 또는 비밀번호가 올바르지 않습니다');
        } else {
          Alert.alert('오류', '로그인 처리 중 오류가 발생했습니다');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      width: '100%',
      padding: width * 0.045,
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: width * 0.04,
    },
    contentContainer: {
      flex: 1,
      justifyContent: 'center',
    },
    loginCard: {
      backgroundColor: 'white',
      borderRadius: width * 0.025,
      padding: width * 0.045,
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
    },
    characterImage: {
      width: width * 0.4,
      height: width * 0.4,
      alignSelf: 'center',
      marginBottom: width * 0.03,
    },
    inputContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      borderRadius: width * 0.015,
      backgroundColor: '#F5F6FF',
      padding: width * 0.035,
      marginBottom: width * 0.02,
    },
    input: {
      flex: 1,
      fontSize: width * 0.04,
      marginLeft: width * 0.02,
      color: '#333',
    },
    loginButton: {
      backgroundColor: '#2D5BFF',
      padding: width * 0.035,
      borderRadius: width * 0.015,
      alignItems: 'center',
      marginTop: width * 0.03,
    },
    forgotPassword: {
      alignSelf: 'center',
      marginTop: 16,
    },
    errorText: {
      color: '#ff4444',
      fontSize: width * 0.035,
      marginTop: 4,
      marginLeft: width * 0.02,
    },
    titleText: {
      fontSize: width * 0.055,
      fontWeight: 'bold',
      marginBottom: width * 0.035,
      textAlign: 'center',
      color: '#333',
    },
    buttonText: {
      color: 'white',
      fontSize: width * 0.04,
      fontWeight: 'bold',
      textAlign: 'center',
    },
    forgotPasswordText: {
      color: '#666',
      fontSize: width * 0.04,
      textAlign: 'center',
    }
  });

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <LinearGradient
          colors={['#FFFFFF', '#E6EFFE']}
          locations={[0.19, 1.0]}
          style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0 }}
        />
        <View style={styles.container}>
          <View style={styles.header}>
            <TouchableOpacity onPress={() => navigation.goBack()}>
              <MaterialIcons name="arrow-back-ios" size={iconSize} color="#333" />
            </TouchableOpacity>
          </View>
          <View style={styles.contentContainer}>
            <View style={styles.loginCard}>
              <Image
                source={require('../../assets/verification.png')}
                style={styles.characterImage}
                resizeMode="contain"
              />
              <Text style={styles.titleText}>로그인</Text>
              <View style={styles.inputContainer}>
                <MaterialIcons name="person-outline" size={iconSize} color="#666" />
                <TextInput
                  style={styles.input}
                  placeholder={idFocused ? " " : "아이디를 입력해주세요"}
                  value={id}
                  onChangeText={(text) => {
                    setId(text);
                    setErrors(prev => ({ ...prev, id: '' }));
                  }}
                  onFocus={() => setIdFocused(true)}
                  onBlur={() => setIdFocused(false)}
                  autoCapitalize="none"
                  returnKeyType="next"
                  onSubmitEditing={() => passwordInputRef.current?.focus()}
                  placeholderTextColor="#999"
                />
              </View>
              {errors.id ? <Text style={styles.errorText}>{errors.id}</Text> : null}
              <View style={styles.inputContainer}>
                <MaterialIcons name="lock-outline" size={iconSize} color="#666" />
                <TextInput
                  ref={passwordInputRef}
                  style={styles.input}
                  placeholder={passwordFocused ? " " : "비밀번호를 입력해주세요"}
                  value={password}
                  onChangeText={(text) => {
                    setPassword(text);
                    setErrors(prev => ({ ...prev, password: '' }));
                  }}
                  onFocus={() => setPasswordFocused(true)}
                  onBlur={() => setPasswordFocused(false)}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  returnKeyType="done"
                  onSubmitEditing={handleLogin}
                  placeholderTextColor="#999"
                />
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                  <MaterialIcons 
                    name={showPassword ? "visibility" : "visibility-off"} 
                    size={iconSize} 
                    color="#666" 
                  />
                </TouchableOpacity>
              </View>
              {errors.password ? <Text style={styles.errorText}>{errors.password}</Text> : null}
              <TouchableOpacity 
                style={[styles.loginButton, { opacity: isLoading ? 0.7 : 1 }]}
                onPress={handleLogin}
                disabled={isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={styles.buttonText}>로그인</Text>
                )}
              </TouchableOpacity>
              <TouchableOpacity style={styles.forgotPassword}>
                <Text style={styles.forgotPasswordText}>아이디/비밀번호 찾기</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </MobileContainer>
    </AppWrapper>
  );
};

export default LoginScreen; 