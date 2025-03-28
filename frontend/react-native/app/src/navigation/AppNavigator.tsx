import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';
import SavingsJoinScreen from '../screens/SavingsJoinScreen';
import ServiceScreen from '../screens/ServiceScreen';
import TabNavigator from './TabNavigator';

export type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  SavingsJoin: undefined;
  Service: undefined;
  Main: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="SavingsJoin" component={SavingsJoinScreen} />
        <Stack.Screen name="Service" component={ServiceScreen} />
        <Stack.Screen name="Main" component={TabNavigator} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator; 