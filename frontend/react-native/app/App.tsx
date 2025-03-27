import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Platform } from 'react-native';
import { ThemeProvider } from 'styled-components/native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { RootSiblingParent } from 'react-native-root-siblings';
import { theme } from './src/styles/theme';
import HomeScreen from './src/screens/HomeScreen';
import LoginScreen from './src/screens/LoginScreen';
import SavingsJoinScreen from './src/screens/SavingsJoinScreen';

const Stack = createStackNavigator();

const linking = {
  prefixes: [],
  config: {
    screens: {
      Home: '',
      Login: 'login',
      SavingsJoin: 'savings-join'
    }
  }
};

export default function App() {
  return (
    <SafeAreaProvider>
      <RootSiblingParent>
        <ThemeProvider theme={theme}>
          <StatusBar style="auto" />
          <NavigationContainer linking={Platform.OS === 'web' ? linking : undefined}>
            <Stack.Navigator
              initialRouteName="Home"
              screenOptions={{
                headerShown: false,
                cardStyle: { 
                  backgroundColor: 'transparent',
                  maxWidth: Platform.OS === 'web' ? 390 : '100%',
                  alignSelf: 'center'
                },
                cardStyleInterpolator: ({ current }) => ({
                  cardStyle: {
                    opacity: current.progress
                  }
                }),
                transitionSpec: {
                  open: {
                    animation: 'timing',
                    config: {
                      duration: 300
                    }
                  },
                  close: {
                    animation: 'timing',
                    config: {
                      duration: 300
                    }
                  }
                }
              }}
            >
              <Stack.Screen name="Home" component={HomeScreen} />
              <Stack.Screen name="Login" component={LoginScreen} />
              <Stack.Screen name="SavingsJoin" component={SavingsJoinScreen} />
            </Stack.Navigator>
          </NavigationContainer>
        </ThemeProvider>
      </RootSiblingParent>
    </SafeAreaProvider>
  );
}
