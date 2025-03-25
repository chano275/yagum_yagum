<<<<<<< HEAD
import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Platform } from 'react-native';
import { ThemeProvider } from 'styled-components/native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { theme } from './src/styles/theme';
import HomeScreen from './src/screens/HomeScreen';
import LoginScreen from './src/screens/LoginScreen';

const Stack = createStackNavigator();
=======
import { StatusBar } from "expo-status-bar";
import { ThemeProvider } from "styled-components/native";
import styled from "styled-components/native";
import { theme } from "./src/styles/theme";
import { useFonts } from "expo-font";

// 스타일 컴포넌트 정의
const Container = styled.View`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  justify-content: center;
  align-items: center;
`;

const Title = styled.Text`
  font-size: ${({ theme }) => theme.fontSize.xxl};
  color: ${({ theme }) => theme.colors.text};
  font-weight: bold;
  font-family: "Pretendard-Bold";
`;

const StyledButton = styled.TouchableOpacity`
  background-color: ${({ theme }) => theme.colors.primary};
  padding: ${({ theme }) => theme.spacing.md};
  border-radius: 8px;
  margin-top: ${({ theme }) => theme.spacing.lg};
`;

const ButtonText = styled.Text`
  color: white;
  font-size: ${({ theme }) => theme.fontSize.md};
  font-family: "Pretendard-Regular";
`;
>>>>>>> adf3d1e48331c6eaef31cfaf12a9caaac1666b99

export default function App() {
  const [fontsLoaded] = useFonts({
    "Pretendard-Bold": require("./assets/fonts/Pretendard-Bold.otf"),
    "Pretendard-Light": require("./assets/fonts/Pretendard-Light.otf"),
    "Pretendard-Medium": require("./assets/fonts/Pretendard-Medium.otf"),
    "Pretendard-Regular": require("./assets/fonts/Pretendard-Regular.otf"),
  });

  if (!fontsLoaded) {
    return null; // 폰트가 로드되지 않았을 때 빈 화면 표시
  }

  return (
    <ThemeProvider theme={theme}>
      <NavigationContainer>
        <StatusBar style="auto" />
        <Stack.Navigator 
          initialRouteName="Home"
          screenOptions={{
            headerShown: false,
            cardStyleInterpolator: ({ current, layouts, next }) => {
              const mobileWidth = Platform.OS === 'web' ? 390 : layouts.screen.width;
              const progress = next?.progress;
              
              return {
                cardStyle: {
                  transform: [
                    {
                      translateX: current.progress.interpolate({
                        inputRange: [0, 1],
                        outputRange: [mobileWidth, 0],
                      }),
                    },
                  ],
                },
                ...(progress && {
                  containerStyle: {
                    transform: [
                      {
                        translateX: progress.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0, -mobileWidth/3],
                        }),
                      },
                    ],
                  },
                }),
              };
            },
          }}
        >
          <Stack.Screen name="Home" component={HomeScreen} />
          <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </ThemeProvider>
  );
}
