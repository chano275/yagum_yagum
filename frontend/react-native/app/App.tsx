// App.tsx
import "@expo/metro-runtime";
import React, { useEffect } from "react";
import { Platform, LogBox } from "react-native";
import { ThemeProvider } from "styled-components/native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { RootSiblingParent } from "react-native-root-siblings";
import { useFonts } from "expo-font";
import { theme } from "./src/styles/theme";
import { DimensionProvider } from "./src/context/DimensionContext";
import { TeamProvider } from "./src/context/TeamContext";
import { JoinProvider } from "./src/context/JoinContext";
import { AccountProvider } from "./src/context/AccountContext";
import AppNavigator from "./src/navigation/AppNavigator";
import axios from "axios";
import { useStore } from "./src/store/useStore";

// API 기본 URL 설정
const BASE_URL = 'http://localhost:8000';  // 개발 환경

// 배포 환경용
// const BASE_URL = 'http://3.38.183.156:8000';  // 배포 환경

axios.defaults.baseURL = BASE_URL;

// 안전한 개발을 위해 tintColor 경고 무시
LogBox.ignoreLogs(["Image: style.tintColor is deprecated"]);

export default function App() {
  const { setAuth } = useStore();
  const [fontsLoaded] = useFonts({
    "Pretendard-Bold": require("./assets/fonts/Pretendard-Bold.otf"),
    "Pretendard-Light": require("./assets/fonts/Pretendard-Light.otf"),
    "Pretendard-Medium": require("./assets/fonts/Pretendard-Medium.otf"),
    "Pretendard-Regular": require("./assets/fonts/Pretendard-Regular.otf"),
  });

  useEffect(() => {
    // 앱 시작시 localStorage 체크
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setAuth(token, user);
      } catch (error) {
        console.error('Failed to parse user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  if (!fontsLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <RootSiblingParent>
        <ThemeProvider theme={theme}>
          <DimensionProvider>
            <TeamProvider>
              <JoinProvider>
                <AccountProvider>
                  <StatusBar style="auto" />
                  <AppNavigator />
                </AccountProvider>
              </JoinProvider>
            </TeamProvider>
          </DimensionProvider>
        </ThemeProvider>
      </RootSiblingParent>
    </SafeAreaProvider>
  );
}
