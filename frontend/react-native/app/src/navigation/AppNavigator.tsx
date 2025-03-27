// src/navigation/AppNavigator.tsx
import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import HomeScreen from "../screens/HomeScreen";
import TabNavigator from "./TabNavigator";

const Stack = createStackNavigator();

const AppNavigator = () => {
  return (
    <Stack.Navigator
      initialRouteName="HomeScreen" // "Home"에서 "HomeScreen"으로 변경
      screenOptions={{ headerShown: false }}
    >
      <Stack.Screen
        name="HomeScreen" // "Home"에서 "HomeScreen"으로 변경
        component={HomeScreen}
      />
      <Stack.Screen name="Main" component={TabNavigator} />
    </Stack.Navigator>
  );
};

export default AppNavigator;
