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
import Verifyticket from "../screens/Benefits/VerifyticketScreen";
import AccountSelectScreen from "../screens/AccountSelectScreen";
import CompletionScreen from "../screens/CompletionScreen";
import SavingsGoalScreen from "../screens/SavingsGoalScreen";
import RuleSettingScreen from "../screens/RuleSettingScreen";
import History from "../screens/History";
import TransferScreen from "../screens/TransferScreen";
import TransactionDetailScreen from "@/screens/TransactionDetailScreen";
import TransferCompleteScreen from "../screens/TransferCompleteScreen";

export type RootStackParamList = {
  Home: undefined;
  Main: undefined;
  Login: undefined;
  SavingsJoin: undefined;
  Transfer: undefined;
  TransferComplete: undefined;
  History: undefined;
  Service: undefined;
  PlayerSelect: undefined;
  SavingsGoal: undefined;
  RuleSetting: undefined;
  AccountSelect: undefined;
  Completion: undefined;
  Matchrank: undefined;
  Merchdiscount: undefined;
  Primerate: undefined;
  Verifyticket: undefined;
  TransactionDetail: { id: string };
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
        <Stack.Screen name="SavingsGoal" component={SavingsGoalScreen} />
        <Stack.Screen name="RuleSetting" component={RuleSettingScreen} />
        <Stack.Screen name="AccountSelect" component={AccountSelectScreen} />
        <Stack.Screen name="Completion" component={CompletionScreen} />
        <Stack.Screen name="Matchrank" component={Matchrank} />
        <Stack.Screen name="Verifyticket" component={Verifyticket} />
        <Stack.Screen
          name="TransactionDetail"
          component={TransactionDetailScreen}
        />
        <Stack.Screen name="History" component={History} />
        <Stack.Screen name="Transfer" component={TransferScreen} />
        <Stack.Screen name="TransferComplete" component={TransferCompleteScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
