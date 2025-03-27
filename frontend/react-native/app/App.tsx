// App.tsx
import "@expo/metro-runtime";
import React from "react";
import { StatusBar } from "expo-status-bar";
import { ThemeProvider } from "styled-components/native";
import { theme } from "./src/styles/theme";
import { useFonts } from "expo-font";
import { NavigationContainer } from "@react-navigation/native";
import { DimensionProvider } from "./src/context/DimensionContext";
import AppNavigator from "./src/navigation/AppNavigator";
import { TeamProvider } from "@/context/TeamContext";
import { LogBox } from "react-native"; // 경고 무시용

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
    <ThemeProvider theme={theme}>
      <DimensionProvider>
        <TeamProvider>
          <NavigationContainer>
            <AppNavigator />
          </NavigationContainer>
        </TeamProvider>
      </DimensionProvider>
    </ThemeProvider>
  );
}
