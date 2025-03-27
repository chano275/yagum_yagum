// App.tsx
import "@expo/metro-runtime";
import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Platform, LogBox } from "react-native";
import { ThemeProvider } from "styled-components/native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { RootSiblingParent } from "react-native-root-siblings";
import { useFonts } from "expo-font";
import { theme } from "./src/styles/theme";
import { DimensionProvider } from "./src/context/DimensionContext";
import { TeamProvider } from "@/context/TeamContext";
import HomeScreen from "./src/screens/HomeScreen";
import LoginScreen from "./src/screens/LoginScreen";
import AppNavigator from "./src/navigation/AppNavigator";

// 안전한 개발을 위해 tintColor 경고 무시
LogBox.ignoreLogs(["Image: style.tintColor is deprecated"]);

const Stack = createNativeStackNavigator();

const linking = {
  prefixes: [],
  config: {
    screens: {
      Home: "",
      Login: "login",
      Main: "main", // AppNavigator를 위한 라우트 추가
    },
  },
};

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
              <NavigationContainer
                linking={Platform.OS === "web" ? linking : undefined}
              >
                <Stack.Navigator
                  initialRouteName="Home"
                  screenOptions={{
                    headerShown: false,
                    animation: "slide_from_right",
                  }}
                >
                  <Stack.Screen name="Home" component={HomeScreen} />
                  <Stack.Screen name="Login" component={LoginScreen} />
                  <Stack.Screen name="Main" component={AppNavigator} />
                </Stack.Navigator>
              </NavigationContainer>
            </TeamProvider>
          </DimensionProvider>
        </ThemeProvider>
      </RootSiblingParent>
    </SafeAreaProvider>
  );
}
