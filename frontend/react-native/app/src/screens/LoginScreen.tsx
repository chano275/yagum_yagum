import React, { useState, useRef } from "react";
import {
  View,
  TextInput,
  TouchableOpacity,
  Platform,
  useWindowDimensions,
  Alert,
  ActivityIndicator,
  TextInputProps,
  StyleSheet,
  Image,
  Text,
} from "react-native";
import { MaterialIcons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import {
  AppWrapper,
  MobileContainer as BaseMobileContainer,
  getAdjustedWidth,
  StyledProps as BaseStyledProps,
  BASE_MOBILE_WIDTH,
} from "../constants/layout";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import axios from "axios";
import { useStore } from "../store/useStore";
import { AuthState } from "../store/useStore";
import { useTeam } from "../context/TeamContext";
import { api } from "../api/axios";
import styled from "styled-components/native";
import { Ionicons } from "@expo/vector-icons";

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList, "Login">;

interface MobileContainerProps extends BaseStyledProps {
  insetsTop?: number;
}

const Container = styled.View<BaseStyledProps>`
  flex: 1;
  width: 100%;
  padding: ${({ width }) => {
    const baseWidth = Platform.OS === "web" ? BASE_MOBILE_WIDTH : width;
    return baseWidth * 0.045;
  }}px;
  padding-top: ${Platform.OS === "web" ? "8px" : "0px"};
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.View`
  flex: 1;
  justify-content: center;
  align-items: center;
`;

const Header = styled.View<BaseStyledProps>`
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: ${(props) => props.width * 0.04}px;
  padding-left: 0;
  margin-top: ${Platform.OS === "web" ? "16px" : "8px"};
`;

const MobileContainer = styled(BaseMobileContainer)<MobileContainerProps>`
  padding-top: ${props => Platform.OS === "web" ? "12px" : `${props.insetsTop || 0}px`};
`;

const BackButton = styled.TouchableOpacity`
  padding: 10px 8px 10px 0;
  justify-content: center;
  align-items: center;
`;

const LoginScreen = () => {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [idFocused, setIdFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({
    id: "",
    password: "",
  });
  const [loginError, setLoginError] = useState("");
  const { setTeamData } = useTeam();

  const navigation = useNavigation<NavigationProp>();
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const iconSize = width * 0.055;
  const passwordInputRef = useRef<TextInput>(null);
  const setAuth = useStore((state: AuthState) => state.setAuth);

  const validateInputs = () => {
    const newErrors = {
      id: "",
      password: "",
    };

    if (!id.trim()) newErrors.id = "아이디를 입력해주세요";
    if (!password.trim()) newErrors.password = "비밀번호를 입력해주세요";

    setErrors(newErrors);
    // 에러 메시지 중 하나만 보여주기 위한 처리
    if (newErrors.id) {
      setLoginError(newErrors.id);
    } else if (newErrors.password) {
      setLoginError(newErrors.password);
    } else {
      setLoginError("");
    }

    return !newErrors.id && !newErrors.password;
  };

  const handleLogin = async () => {
    if (!validateInputs()) return;

    setIsLoading(true);
    setLoginError(""); // 로그인 시도 시 이전 에러 메시지 초기화

    try {
      const formData = new FormData();
      formData.append("username", id);
      formData.append("password", password);

      const response = await api.post('/api/user/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        const { access_token, token_type, team } = response.data;
        // 인증 정보 저장
        setAuth(access_token, { id: id, name: id });

        // 팀 정보가 있으면 TeamContext에 설정
        if (team) {
          setTeamData(team);
        }

        navigation.replace("Home");
      }
    } catch (error) {
      if (error instanceof Error) {
        console.error('Login failed:', error);
        // Alert 대신 상태에 에러 메시지 저장
        setLoginError("아이디 또는 비밀번호가 올바르지 않습니다.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      width: "100%",
      padding: width * 0.045,
    },
    header: {
      flexDirection: "row",
      alignItems: "center",
      marginBottom: width * 0.04,
    },
    contentContainer: {
      flex: 1,
      justifyContent: "center",
      alignItems: "center",
      paddingBottom: Platform.OS === "web" ? width * 0.1 : 0,
    },
    loginCard: {
      backgroundColor: "white",
      borderRadius: width * 0.025,
      padding: width * 0.05,
      width: "100%",
      maxWidth: 420,
      alignSelf: "center",
      transform: [{ translateY: Platform.OS === "web" ? -width * 0.08 : 0 }],
      ...Platform.select({
        ios: {
          shadowColor: "#000",
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.08,
          shadowRadius: 6,
        },
        android: {
          elevation: 3,
        },
        web: {
          boxShadow: "0px 2px 8px rgba(0, 0, 0, 0.08)",
        },
      }),
    },
    characterImage: {
      width: width * 0.35,
      height: width * 0.35,
      alignSelf: "center",
      marginBottom: width * 0.04,
    },
    inputContainer: {
      flexDirection: "row",
      alignItems: "center",
      borderRadius: width * 0.015,
      backgroundColor: "#F5F6FF",
      padding: width * 0.04,
      marginBottom: width * 0.025,
      ...Platform.select({
        ios: {
          shadowColor: "#000",
          shadowOffset: { width: 0, height: 1 },
          shadowOpacity: 0.05,
          shadowRadius: 2,
        },
        android: {
          elevation: 1,
        },
        web: {
          boxShadow: "0px 1px 2px rgba(0, 0, 0, 0.05)",
        },
      }),
    },
    focusedInputContainer: {
      backgroundColor: "#FFFFFF",
      ...Platform.select({
        ios: {
          shadowColor: "#2D5BFF",
          shadowOffset: { width: 0, height: 0 },
          shadowOpacity: 0.2,
          shadowRadius: 3,
        },
        android: {
          elevation: 2,
        },
        web: {
          boxShadow:
            "0px 0px 0px 2px rgba(45, 91, 255, 0.2), 0px 1px 2px rgba(0, 0, 0, 0.05)",
        },
      }),
    },
    input: {
      flex: 1,
      fontSize: width * 0.042,
      marginLeft: width * 0.025,
      color: "#333",
      ...Platform.select({
        web: {
          outlineStyle: "none",
        },
      }),
    },
    loginButton: {
      backgroundColor: "#2D5BFF",
      padding: width * 0.04,
      borderRadius: width * 0.015,
      alignItems: "center",
      marginTop: width * 0.03,
    },
    errorText: {
      color: "#ff4444",
      fontSize: width * 0.035,
      marginTop: 4,
      marginLeft: width * 0.02,
      marginBottom: width * 0.02,
    },
    titleText: {
      fontSize: width * 0.06,
      fontWeight: "bold",
      marginBottom: width * 0.04,
      textAlign: "center",
      color: "#333",
    },
    buttonText: {
      color: "white",
      fontSize: width * 0.042,
      fontWeight: "bold",
      textAlign: "center",
    },
    loginErrorContainer: {
      height: width * 0.005, 
      justifyContent: 'center',
      alignItems: 'center',
      marginTop: width * 0.005,
      marginBottom: width * 0.005,
    },
    loginErrorText: {
      color: "#ff4444",
      fontSize: width * 0.03,
      textAlign: "center",
    },
  });

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <LinearGradient
          colors={["#FFFFFF", "#E6EFFE"]}
          locations={[0.19, 1.0]}
          style={{ position: "absolute", left: 0, right: 0, top: 0, bottom: 0 }}
        />
        <Container width={width}>
          <Header width={width}>
            <BackButton onPress={() => navigation.goBack()}>
              <Ionicons name="chevron-back" size={24} color="#000" />
            </BackButton>
          </Header>
          <MainContent>
            <View style={styles.loginCard}>
              <Image
                source={require("../../assets/verification.png")}
                style={styles.characterImage}
                resizeMode="contain"
              />
              <Text style={styles.titleText}>로그인</Text>
              <View
                style={[
                  styles.inputContainer,
                  idFocused && styles.focusedInputContainer,
                ]}
              >
                <MaterialIcons
                  name="person-outline"
                  size={iconSize}
                  color="#666"
                />
                <TextInput
                  style={styles.input}
                  placeholder={idFocused ? " " : "아이디를 입력해주세요"}
                  value={id}
                  onChangeText={(text) => {
                    setId(text);
                    setErrors((prev) => ({ ...prev, id: "" }));
                    // 아이디를 입력하면 해당 에러 메시지는 지우지만, 다른 에러는 유지
                    if (loginError === "아이디를 입력해주세요") {
                      setLoginError("");
                    }
                  }}
                  onFocus={() => setIdFocused(true)}
                  onBlur={() => setIdFocused(false)}
                  autoCapitalize="none"
                  returnKeyType="next"
                  onSubmitEditing={() => passwordInputRef.current?.focus()}
                  placeholderTextColor="#999"
                />
              </View>
              <View
                style={[
                  styles.inputContainer,
                  passwordFocused && styles.focusedInputContainer,
                ]}
              >
                <MaterialIcons
                  name="lock-outline"
                  size={iconSize}
                  color="#666"
                />
                <TextInput
                  ref={passwordInputRef}
                  style={styles.input}
                  placeholder={
                    passwordFocused ? " " : "비밀번호를 입력해주세요"
                  }
                  value={password}
                  onChangeText={(text) => {
                    setPassword(text);
                    setErrors((prev) => ({ ...prev, password: "" }));
                    // 비밀번호를 입력하면 해당 에러 메시지는 지우지만, 다른 에러는 유지
                    if (loginError === "비밀번호를 입력해주세요") {
                      setLoginError("");
                    }
                  }}
                  onFocus={() => setPasswordFocused(true)}
                  onBlur={() => setPasswordFocused(false)}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  returnKeyType="done"
                  onSubmitEditing={handleLogin}
                  placeholderTextColor="#999"
                />
                <TouchableOpacity
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <MaterialIcons
                    name={showPassword ? "visibility" : "visibility-off"}
                    size={iconSize}
                    color="#666"
                  />
                </TouchableOpacity>
              </View>
              {/* 통합 에러 메시지 공간 */}
              <View style={styles.loginErrorContainer}>
                {loginError ? (
                  <Text style={styles.loginErrorText}>{loginError}</Text>
                ) : null}
              </View>
              
              <TouchableOpacity
                style={styles.loginButton}
                onPress={handleLogin}
                disabled={isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={styles.buttonText}>로그인</Text>
                )}
              </TouchableOpacity>
            </View>
          </MainContent>
        </Container>
      </MobileContainer>
    </AppWrapper>
  );
};

export default LoginScreen;
