import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HomeScreen from "../screens/HomeScreen";
import LoginScreen from "../screens/LoginScreen";
import SavingsJoinScreen from "../screens/SavingsJoinScreen";
import ServiceScreen from "../screens/ServiceScreen";
import TabNavigator from "./TabNavigator";
import { useStore } from "../store/useStore";
import PlayerSelectScreen from "../screens/PlayerSelectScreen";
import Matchrank from "../screens/Benefits/MatchrankScreen";
import Merchdiscount from "../screens/Benefits/MerchdiscountScreen";
import Primerate from "../screens/Benefits/PrimerateScreen";
import Verifyticket from "../screens/Benefits/VerifyticketScreen";

export type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  SavingsJoin: undefined;
  Service: undefined;
  Main: undefined;
  PlayerSelect: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const AppNavigator = () => {
  const { isLoggedIn } = useStore();

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="SavingsJoin" component={SavingsJoinScreen} />
        <Stack.Screen name="Service" component={ServiceScreen} />
        <Stack.Screen name="Main" component={TabNavigator} />
        <Stack.Screen name="PlayerSelect" component={PlayerSelectScreen} />
        <Stack.Screen name="Matchrank" component={Matchrank} />
        <Stack.Screen name="Merchdiscount" component={Merchdiscount} />
        <Stack.Screen name="Primerate" component={Primerate} />
        <Stack.Screen name="Verifyticket" component={Verifyticket} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
