// App.tsx
import "@expo/metro-runtime";
import React from "react";
import { Platform, LogBox } from "react-native";
import { ThemeProvider } from "styled-components/native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { RootSiblingParent } from "react-native-root-siblings";
import { useFonts } from "expo-font";
import { theme } from "./src/styles/theme";
import { DimensionProvider } from "./src/context/DimensionContext";
import { TeamProvider } from "./src/context/TeamContext";
import AppNavigator from "./src/navigation/AppNavigator";
import axios from "axios";

const BASE_URL = __DEV__
  ? "http://localhost:8000" // 개발 환경
  : "http://3.38.183.156:8000"; // 배포 환경

axios.defaults.baseURL = BASE_URL;

// 안전한 개발을 위해 tintColor 경고 무시
LogBox.ignoreLogs(["Image: style.tintColor is deprecated"]);

export default function App() {
  const [fontsLoaded] = useFonts({
    "Pretendard-Bold": require("./assets/fonts/Pretendard-Bold.otf"),
    "Pretendard-Light": require("./assets/fonts/Pretendard-Light.otf"),
    "Pretendard-Medium": require("./assets/fonts/Pretendard-Medium.otf"),
    "Pretendard-Regular": require("./assets/fonts/Pretendard-Regular.otf"),
  });

  if (!fontsLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <RootSiblingParent>
        <ThemeProvider theme={theme}>
          <DimensionProvider>
            <TeamProvider>
              <StatusBar style="auto" />
              <AppNavigator />
            </TeamProvider>
          </DimensionProvider>
        </ThemeProvider>
      </RootSiblingParent>
    </SafeAreaProvider>
  );
}
