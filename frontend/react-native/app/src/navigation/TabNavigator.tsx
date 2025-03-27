import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "../styles/theme";
import MainPage from "../screens/MainPageScreen";
import SavingsScreen from "../screens/SavingsScreen";
import ReportScreen from "../screens/ReportScreen";
import BenefitsScreen from "../screens/BenefitsScreen";
import { useDimension } from "../context/DimensionContext";
import { useTeam } from "../context/TeamContext"; // TeamContext 추가
import { Platform, View } from "react-native";

const Tab = createBottomTabNavigator();

const TabNavigator = () => {
  const { width } = useDimension();
  const { teamColor } = useTeam(); // 팀 색상 가져오기

  return (
    <View
      style={{
        flex: 1,
        maxWidth: width,
        width: "100%",
        alignSelf: "center",
        position: "relative",
      }}
    >
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarStyle: {
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            width: "100%",
            backgroundColor: "white",
            borderTopWidth: 1,
            borderTopColor: "#eeeeee",
            height: 60,
            elevation: 0,
            shadowOpacity: 0,
            shadowOffset: { width: 0, height: 0 },
            shadowRadius: 0,
          },
          // 하드코딩된 색상을 teamColor로 변경
          tabBarActiveTintColor: teamColor.primary, // 팀 색상 동적 적용
          tabBarInactiveTintColor: "#333333",
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: "500",
            marginBottom: 5,
          },
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

            if (route.name === "홈") {
              iconName = focused ? "home" : "home-outline";
            } else if (route.name === "적금내역") {
              iconName = focused ? "wallet" : "wallet-outline";
            } else if (route.name === "리포트") {
              iconName = focused ? "stats-chart" : "stats-chart-outline";
            } else if (route.name === "혜택") {
              iconName = focused ? "gift" : "gift-outline";
            }

            return <Ionicons name={iconName} size={24} color={color} />;
          },
        })}
        sceneContainerStyle={{
          backgroundColor: "transparent",
        }}
      >
        <Tab.Screen name="홈" component={MainPage} />
        <Tab.Screen name="적금내역" component={SavingsScreen} />
        <Tab.Screen name="리포트" component={ReportScreen} />
        <Tab.Screen name="혜택" component={BenefitsScreen} />
      </Tab.Navigator>
    </View>
  );
};

export default TabNavigator;
