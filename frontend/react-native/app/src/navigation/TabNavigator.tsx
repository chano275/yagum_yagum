import React from "react";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "../styles/theme";
import MainPage from "@/screens/MainPageScreen";
import SavingsScreen from "@/screens/SavingsScreen";
import ReportScreen from "@/screens/ReportScreen";
import BenefitsScreen from "@/screens/BenefitsScreen";
import { useDimension } from "../context/DimensionContext";
import { useTeam } from "../context/TeamContext";
import { Platform, View } from "react-native";

const Tab = createBottomTabNavigator();

const TabNavigator = () => {
  const { width } = useDimension();
  const { teamColor } = useTeam();

  const deviceWidth = Platform.OS === "web" ? 390 : Math.min(width, 430);

  return (
    <View
      style={{
        flex: 1,
        maxWidth: deviceWidth,
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
            height: Platform.OS === "ios" ? 65 : 50,
            paddingBottom: Platform.OS === "ios" ? 15 : 5,
            elevation: 0,
            shadowOpacity: 0,
            shadowOffset: { width: 0, height: 0 },
            shadowRadius: 0,
          },
          tabBarActiveTintColor: teamColor.primary,
          tabBarInactiveTintColor: "#333333",
          tabBarLabelStyle: {
            fontSize: 10,
            fontWeight: "500",
            marginBottom: Platform.OS === "ios" ? 0 : 3,
          },
          tabBarIcon: ({ focused, color, size }) => {
            let iconName: keyof typeof Ionicons.glyphMap = "home";

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
          backgroundColor: "#f8f9fa",
        }}
      >
        <Tab.Screen name="홈" component={MainPage} />
        <Tab.Screen
          name="적금내역"
          component={SavingsScreen}
          listeners={({ navigation }) => ({
            tabPress: (e) => {
              e.preventDefault(); // 기본 동작 방지
              navigation.navigate("적금내역", { viewMode: "calendar" }); // 항상 캘린더로 초기화
            },
          })}
        />
        <Tab.Screen name="리포트" component={ReportScreen} />
        <Tab.Screen name="혜택" component={BenefitsScreen} />
      </Tab.Navigator>
    </View>
  );
};

export default TabNavigator;
