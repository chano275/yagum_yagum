import React, { useState, useEffect, useRef } from "react";
import {
  useWindowDimensions,
  SafeAreaView,
  ScrollView,
  Platform,
  Pressable,
  View,
  Text,
  Animated,
  Image,
  Alert,
  ActivityIndicator,
  TouchableOpacity,
  Dimensions,
} from "react-native";
import { Ionicons, MaterialIcons } from "@expo/vector-icons";
import styled from "styled-components/native";
import { LinearGradient } from "expo-linear-gradient";
import {
  AppWrapper,
  MobileContainer as BaseMobileContainer,
  getAdjustedWidth,
  StyledProps as BaseStyledProps,
  BASE_MOBILE_WIDTH,
} from "../constants/layout";
import * as Haptics from "expo-haptics";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useStore } from "../store/useStore";
import * as Clipboard from "expo-clipboard";
import Toast from "react-native-root-toast";
import { useAccountStore } from "../store/useStore";
import { RootStackParamList } from "../navigation/AppNavigator";
import { useTeam } from "../context/TeamContext";
import { teamColors, teamIdToCode, teamNameToCode } from "../styles/teamColors";
import { useSafeAreaInsets } from 'react-native-safe-area-context';

type NavigationProp = NativeStackNavigationProp<RootStackParamList, "Home">;

interface StyledProps extends BaseStyledProps {
  insetsTop?: number;
  insetsBottom?: number;
}

const Container = styled.View<BaseStyledProps>`
  flex: 1;
  width: 100%;
  padding: ${({ width }) => {
    const baseWidth = Platform.OS === "web" ? BASE_MOBILE_WIDTH : width;
    return baseWidth * 0.045;
  }}px;
  padding-top: 0;
`;

const Header = styled.View<BaseStyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${(props) => props.width * 0.04}px;
  margin-top: ${Platform.OS === "web" ? "16px" : "0px"};
`;

const HeaderTitle = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.06}px;
  font-weight: bold;
  color: #333;
`;

const IconContainer = styled.View`
  flex-direction: row;
  align-items: center;
`;

const IconButton = styled.TouchableOpacity<BaseStyledProps>`
  padding: ${({ width }) => width * 0.02}px;
  margin-left: ${({ width }) => width * 0.02}px;
`;

const ServiceCardWrapper = styled.TouchableOpacity<BaseStyledProps>`
  background-color: #f0f2ff;
  border-radius: ${({ width }) => width * 0.025}px;
  padding: ${(props) => props.width * 0.045}px;
  margin-bottom: ${(props) => props.width * 0.025}px;
  width: 100%;
  ${Platform.select({
    ios: {
      shadowColor: "#2D5BFF",
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.08,
      shadowRadius: 4,
    },
    android: {
      elevation: 2,
    },
    web: {
      boxShadow: "0 2px 4px rgba(45, 91, 255, 0.08)",
    },
  })}
`;

const webStyles =
  Platform.OS === "web"
    ? {
  serviceCard: {
          transition: "all 0.2s ease-in-out",
          ":hover": {
            transform: "scale(1.01)",
            boxShadow: "0 4px 12px rgba(107, 119, 248, 0.15)",
            cursor: "pointer",
          },
  },
  startButton: {
          transition: "all 0.2s ease-in-out",
          ":hover": {
            transform: "scale(1.02)",
      opacity: 0.95,
            cursor: "pointer",
          },
  },
  iconButton: {
          transition: "all 0.2s ease-in-out",
          ":hover": {
            transform: "scale(1.1)",
      opacity: 0.8,
            cursor: "pointer",
          },
        },
    }
    : {};

const ServiceTitleContainer = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
`;

const ContentContainer = styled.View`
  flex-direction: row;
  align-items: center;
  gap: 8px;
  flex: 1;
`;

const ServiceTextContainer = styled.View<BaseStyledProps>`
  flex: 1;
  padding-right: 0;
`;

const ServiceIcon = styled.Image`
  width: 40px;
  height: 40px;
  margin-right: 4px;
`;

const ServiceTitle = styled.Text<BaseStyledProps>`
  font-size: ${(props: BaseStyledProps) => Math.min(props.width * 0.045, 24)}px;
  line-height: ${(props: BaseStyledProps) => Math.min(props.width * 0.062, 32)}px;
  font-weight: bold;
  letter-spacing: -0.3px;
  color: #333;
`;

const ColoredText = styled.Text`
  color: #2d5bff;
  font-weight: bold;
`;

const BlackText = styled.Text`
  color: black;
  font-weight: bold;
`;

const LightText = styled.Text`
  color: #999999;
  font-weight: bold;
`;

const ServiceDescription = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => Math.min(width * 0.038, 16)}px;
  line-height: ${({ width }) => Math.min(width * 0.052, 24)}px;
  color: #222222;
  letter-spacing: -0.3px;
`;

const StartButton = styled.TouchableOpacity<BaseStyledProps>`
  background-color: ${({ theme }) => theme.colors.primary};
  padding: ${({ width }) => width * 0.03}px;
  border-radius: ${({ width }) => width * 0.02}px;
  align-items: center;
  margin-top: ${({ width }) => width * 0.025}px;
`;

const ButtonText = styled.Text<BaseStyledProps>`
  color: white;
  font-size: ${({ width }) => Math.min(width * 0.04, 18)}px;
  font-weight: bold;
`;

const RecommendSection = styled.View<BaseStyledProps>`
  margin-top: ${({ width }) => width * 0.0}px;
`;

const SectionTitle = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.046}px;
  font-weight: 900;
  color: #222222;
  margin-bottom: ${({ width }) => width * 0.008}px;
`;

const AuthCard = styled.View<BaseStyledProps>`
  background-color: white;
  border-radius: ${({ width }) => width * 0.025}px;
  padding: ${(props) => props.width * 0.045}px;
  margin-bottom: ${(props) => props.width * 0.05}px;
  width: 100%;
  min-height: ${(props) => props.width * 0.52}px;
  ${Platform.select({
  ios: {
      shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
  },
  android: {
    elevation: 3,
  },
  web: {
      boxShadow: "0px 2px 8px rgba(0, 0, 0, 0.08)",
    },
})}
`;

const AuthCardContent = styled.View`
  flex: 1;
  justify-content: space-between;
`;

const AuthCardHeader = styled.View<BaseStyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-top: ${({ width }) => width * -0.02}px;
`;

const AuthCardBody = styled.View`
  flex: 1;
`;

const AuthCardText = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.0425}px;
  font-weight: bold;
  margin-bottom: 8px;
  line-height: ${({ width }) => width * 0.06}px;
`;

const AuthCardImage = styled.Image<BaseStyledProps>`
  width: ${({ width }) => width * 0.35}px;
  height: ${({ width }) => width * 0.35}px;
  margin-left: ${({ width }) => width * 0.02}px;
  padding-top: ${({ width }) => width * 0.01}px;
`;

const AccountInfo = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 8px;
`;

const AccountRow = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 8px;
`;

const AccountNumberContainer = styled.View`
  flex: 1;
`;

const AccountNumberRow = styled.View`
  flex-direction: row;
  align-items: center;
`;

const AccountTypeText = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.038}px;
  color: #000;
  line-height: ${({ width }) => width * 0.052}px;
  font-weight: 600;
`;

const AccountNumberText = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.038}px;
  color: #666;
  line-height: ${({ width }) => width * 0.052}px;
`;

const CopyButton = styled.TouchableOpacity`
  padding-left: 4px;
  align-items: center;
  justify-content: center;
`;

const BalanceRow = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
`;

const AccountLeftSection = styled.View`
  flex-direction: row;
  align-items: center;
`;

const AccountRightSection = styled.View`
  flex-direction: row;
  align-items: center;
  gap: 8px;
`;

const AccountIcon = styled.Image`
  width: 24px;
  height: 24px;
  margin-right: 8px;
`;

const BalanceContainer = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-top: 0px;
`;

const Balance = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.072}px;
  font-weight: 700;
  color: #000;
  margin: 0;
`;

const ButtonContainer = styled.View`
  flex-direction: row;
  gap: 12px;
  margin-top: 16px;
`;

const ActionButton = styled.TouchableOpacity<BaseStyledProps>`
  flex: 1;
  background-color: #f0f2ff;
  padding: ${({ width }) => width * 0.035}px;
  border-radius: ${({ width }) => width * 0.02}px;
  align-items: center;
`;

const ButtonLabel = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.036}px;
  color: #2d5bff;
  font-weight: 600;
`;

const MobileContainer = styled(BaseMobileContainer)<StyledProps>`
  padding-top: ${props => Platform.OS === "web" ? "24px" : `${props.insetsTop || 0}px`};
`;

const HomeScreen = () => {
  const { width: windowWidth } = useWindowDimensions();
  const width = getAdjustedWidth(windowWidth);
  const iconSize = width * 0.06;
  const navigation = useNavigation<NavigationProp>();
  const { isLoggedIn, logout } = useStore();
  const { accountInfo, isLoading, error, fetchAccountInfo } = useAccountStore();
  const { setTeamData } = useTeam();
  const insets = useSafeAreaInsets();

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideUpAnim = useRef(new Animated.Value(50)).current;
  const firstCardScale = useRef(new Animated.Value(1)).current;
  const recommendCardScale = useRef(new Animated.Value(1)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (isLoggedIn) {
      fetchAccountInfo();
    }
  }, [isLoggedIn, fetchAccountInfo]);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideUpAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideUpAnim]);

  useEffect(() => {
    if (
      isLoggedIn &&
      accountInfo?.savings_accounts &&
      accountInfo.savings_accounts.length > 0
    ) {
      const account = accountInfo.savings_accounts[0];

      if (
        account.team_name &&
        (account.team_name.includes("SSG") ||
          account.team_name.includes("랜더스"))
      ) {
        console.log("[HomeScreen] SSG 랜더스 팀 감지:", account.team_name);

        setTeamData({
          team_id: 6,
          team_name: account.team_name,
          team_color: "#E10600",
          team_color_secondary: "#FFFFFF",
          team_color_background: "#FFB81C",
        });
      }
      else if (account.team_name) {
        const teamCode = teamNameToCode[account.team_name] || "KIA";
        console.log(
          "[HomeScreen] 팀 감지:",
          account.team_name,
          "코드:",
          teamCode
        );

        setTeamData({
          team_id: Object.keys(teamIdToCode).find(
            (key) => teamIdToCode[Number(key)] === teamCode
          )
            ? Number(
                Object.keys(teamIdToCode).find(
                  (key) => teamIdToCode[Number(key)] === teamCode
                )
              )
            : 1,
          team_name: account.team_name,
          team_color: teamColors[teamCode]?.primary || "#2D5BFF",
          team_color_secondary: teamColors[teamCode]?.secondary || "#FFFFFF",
          team_color_background: teamColors[teamCode]?.background || "#FFFFFF",
        });
      }
    }
  }, [isLoggedIn, accountInfo]);

  const onFirstCardPress = () => {
    Animated.sequence([
      Animated.timing(firstCardScale, {
        toValue: 0.98,
        duration: 150,
        useNativeDriver: true,
      }),
      Animated.timing(firstCardScale, {
        toValue: 1,
        duration: 150,
        useNativeDriver: true,
      }),
    ]).start(() => {
      if (Platform.OS !== "web") {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
      handleComponentPress(0);
    });
  };

  const onRecommendCardPress = () => {
    Animated.sequence([
      Animated.timing(recommendCardScale, {
        toValue: 0.97,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(recommendCardScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start(() => {
      if (Platform.OS !== "web") {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
      handleComponentPress(2);
    });
  };

  const onStartButtonPress = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    navigation.navigate("Login");
  };

  const AnimatedServiceCard =
    Animated.createAnimatedComponent(ServiceCardWrapper);
  const AnimatedStartButton = Animated.createAnimatedComponent(StartButton);
  const AnimatedScrollView = Animated.createAnimatedComponent(ScrollView);

  const renderAccountSection = () => {
    return (
      <AnimatedServiceCard
        width={width}
        style={[
          { 
            backgroundColor: "#F0F2FF",
            ...Platform.select({
              ios: {
                shadowColor: "#2D5BFF",
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.08,
                shadowRadius: 4,
              },
              android: {
                elevation: 2,
              },
              web: {
                boxShadow: "0 2px 4px rgba(45, 91, 255, 0.08)",
              },
            }),
          },
          { transform: [{ scale: firstCardScale }] },
        ]}
        onPress={onFirstCardPress}
        activeOpacity={1}
      >
        <ServiceTitleContainer>
          <ContentContainer>
            <ServiceIcon
              source={require("../../assets/baseball.png")}
              style={{ width: 40, height: 40 }}
              resizeMode="contain"
            />
            <ServiceTextContainer width={width}>
              <ServiceTitle width={width}>
                {isLoggedIn ? (
                  <>
                    <Text style={{ fontSize: width * 0.034 }}>
                      <BlackText>
                        {accountInfo?.user_name || "김싸피"}
                      </BlackText>
                      <LightText>님을 위한 맞춤 서비스,</LightText>
                    </Text>
                    {"\n"}
                    <ColoredText>야금야금</ColoredText>
                    <BlackText>적금</BlackText>
                  </>
                ) : (
                  <>
                    <Text style={{ fontSize: width * 0.036 }}>
                      나만의 응원팀으로{"\n"}
                      야금야금 적금 시작하기
                    </Text>
                  </>
                )}
              </ServiceTitle>
            </ServiceTextContainer>
          </ContentContainer>
          <MaterialIcons
            name="chevron-right"
            size={24}
            color="rgba(0, 0, 0, 0.25)"
          />
        </ServiceTitleContainer>
      </AnimatedServiceCard>
    );
  };

  const renderSecondSection = () => {
    return (
      <AuthCard width={width}>
        <AuthCardContent>
          <AuthCardBody>
            {isLoggedIn ? (
              <>
                <AccountRow>
                  <AccountIcon
                    source={require("../../assets/shinhan-icon.png")}
                  />
                  <AccountNumberContainer>
                    <AccountTypeText width={width}>
                      입출금 통장(자유예금)
                    </AccountTypeText>
                    <AccountNumberRow>
                      <AccountNumberText width={width}>
                        {accountInfo?.source_account.account_num ||
                          "111-222-333333"}
                      </AccountNumberText>
                      <CopyButton
                        onPress={async () => {
                          await Clipboard.setStringAsync(
                            accountInfo?.source_account.account_num ||
                              "111-222-333333"
                          );
                          Toast.show("✓ 계좌번호가 복사되었습니다", {
                          duration: Toast.durations.SHORT,
                          position: Toast.positions.BOTTOM,
                          shadow: true,
                          animation: true,
                          hideOnPress: true,
                          delay: 0,
                            backgroundColor: "rgba(45, 45, 45, 0.95)",
                            textColor: "#ffffff",
                          opacity: 0.95,
                          containerStyle: {
                            borderRadius: 16,
                            paddingHorizontal: 20,
                            paddingVertical: 14,
                            marginBottom: 40,
                              flexDirection: "row",
                              alignItems: "center",
                            gap: 8,
                            ...Platform.select({
                              ios: {
                                  shadowColor: "#000",
                                shadowOffset: { width: 0, height: 4 },
                                shadowOpacity: 0.15,
                                shadowRadius: 8,
                              },
                              android: {
                                elevation: 6,
                              },
                              web: {
                                  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                                },
                              }),
                            },
                          });
                        }}
                      >
                        <Ionicons
                          name="copy-outline"
                          size={16}
                          color="rgba(0, 0, 0, 0.35)"
                        />
                      </CopyButton>
                    </AccountNumberRow>
                  </AccountNumberContainer>
                </AccountRow>
                <BalanceRow>
                  <Balance width={width}>
                    {accountInfo?.source_account.total_amount.toLocaleString()}
                    원
                  </Balance>
                </BalanceRow>
              </>
            ) : (
              <AuthCardHeader width={width}>
                <View style={{ flex: 1 }}>
                  <AuthCardText width={width}>
                    간편하게 <Text style={{ color: "#2D5BFF" }}>본인인증</Text>
                    하고{"\n"}
                    서비스를 이용해보세요.
                  </AuthCardText>
                </View>
                <AuthCardImage
                  source={require("../../assets/verification.png")}
                  width={width}
                  resizeMode="contain"
                />
              </AuthCardHeader>
            )}
          </AuthCardBody>
          {isLoggedIn ? (
            <ButtonContainer>
              <ActionButton width={width} onPress={() => navigation.navigate("Transfer")}>
                <ButtonLabel width={width}>이체</ButtonLabel>
              </ActionButton>
              <ActionButton width={width} onPress={() => navigation.navigate("History")}>
                <ButtonLabel width={width}>거래내역</ButtonLabel>
              </ActionButton>
            </ButtonContainer>
          ) : (
            <AnimatedStartButton
              width={width}
              onPress={onStartButtonPress}
              style={{ transform: [{ scale: buttonScale }] }}
            >
              <ButtonText width={width}>시작하기</ButtonText>
            </AnimatedStartButton>
          )}
        </AuthCardContent>
      </AuthCard>
    );
  };

  const handleComponentPress = (index: number) => {
    if ((index === 0 || index === 2) && isLoggedIn) {
      if (
        accountInfo?.savings_accounts &&
        accountInfo.savings_accounts.length > 0
      ) {
        navigation.navigate("Main");
      } else {
        navigation.navigate("SavingsJoin");
      }
    } else if ((index === 0 || index === 2) && !isLoggedIn) {
      navigation.navigate("Login");
    }
  };

  const handleLogout = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    logout();
    Toast.show("로그아웃되었습니다.", {
      duration: Toast.durations.SHORT,
      position: Toast.positions.BOTTOM,
      shadow: true,
      animation: true,
      hideOnPress: true,
      delay: 0,
      backgroundColor: "rgba(45, 45, 45, 0.95)",
      textColor: "#ffffff",
      opacity: 0.95,
      containerStyle: {
        borderRadius: 16,
        paddingHorizontal: 20,
        paddingVertical: 14,
        marginBottom: 40,
        flexDirection: "row",
        alignItems: "center",
        gap: 8,
        ...Platform.select({
          ios: {
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.15,
            shadowRadius: 8,
          },
          android: {
            elevation: 6,
          },
          web: {
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
          },
        }),
      },
    });
  };

  const handleAuthButtonPress = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    if (isLoggedIn) {
      handleLogout();
    } else {
      navigation.navigate("Login");
    }
  };

  return (
    <>
      <AppWrapper>
        <MobileContainer width={width} insetsTop={insets.top}>
          <LinearGradient
            colors={["#FFFFFF", "#E6EFFE"]}
            locations={[0.19, 1.0]}
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              bottom: 0,
            }}
          />
            <AnimatedScrollView
              style={[
                { flex: 1 },
                {
                  opacity: fadeAnim,
                  transform: [{ translateY: slideUpAnim }],
                },
              ]}
              contentContainerStyle={{
                flexGrow: 1,
                width: "100%",
                paddingBottom: insets.bottom,
                paddingTop: 0
              }}
              showsVerticalScrollIndicator={false}
              keyboardShouldPersistTaps="handled"
            >
              <Container width={width}>
                <Header width={width}>
                  <HeaderTitle width={width}>홈</HeaderTitle>
                  <IconContainer>
                  <IconButton width={width} onPress={handleAuthButtonPress}>
                      <MaterialIcons
                        name={isLoggedIn ? "logout" : "login"}
                        size={iconSize}
                        color="black"
                      />
                    </IconButton>
                  </IconContainer>
                </Header>

                {renderAccountSection()}
                {renderSecondSection()}

                <RecommendSection width={width}>
                  <AnimatedServiceCard
                    width={width}
                    style={[
                    { backgroundColor: "#FFFFFF" },
                    { transform: [{ scale: recommendCardScale }] },
                    ]}
                    onPress={onRecommendCardPress}
                    activeOpacity={1}
                >
                  <SectionTitle
                    width={width}
                    style={{ marginBottom: width * 0.005 }}
                  >
                    추천
                  </SectionTitle>
                  {isLoggedIn &&
                  accountInfo?.savings_accounts &&
                  accountInfo.savings_accounts.length > 0 ? (
                    <View style={{ padding: 10 }}>
                      <View
                        style={{
                          flexDirection: "row",
                          justifyContent: "space-between",
                          marginBottom: 10,
                        }}
                      >
                        <Text
                          style={{
                            fontSize: width * 0.045,
                            fontWeight: "bold",
                            color: "#333",
                          }}
                        >
                          {accountInfo.savings_accounts[0].team_name} 적금
                        </Text>
                        <Text
                          style={{ fontSize: width * 0.04, color: "#666" }}
                        >
                          {accountInfo.savings_accounts[0].account_num}
                        </Text>
                      </View>

                      <View
                        style={{
                          flexDirection: "row",
                          justifyContent: "space-between",
                          marginBottom: 10,
                        }}
                      >
                        <Text
                          style={{ fontSize: width * 0.04, color: "#666" }}
                        >
                          현재 적립액
                        </Text>
                        <Text
                          style={{
                            fontSize: width * 0.04,
                            fontWeight: "bold",
                            color: "#333",
                          }}
                        >
                          {accountInfo.savings_accounts[0].total_amount.toLocaleString()}
                          원
                        </Text>
                      </View>

                      <View
                        style={{
                          flexDirection: "row",
                          justifyContent: "space-between",
                          marginBottom: 10,
                        }}
                      >
                        <Text
                          style={{ fontSize: width * 0.04, color: "#666" }}
                        >
                          목표 금액
                        </Text>
                        <Text
                          style={{
                            fontSize: width * 0.04,
                            fontWeight: "bold",
                            color: "#333",
                          }}
                        >
                          {accountInfo.savings_accounts[0].saving_goal.toLocaleString()}
                          원
                        </Text>
                      </View>

                      <View style={{ marginBottom: 5 }}>
                        <Text
                          style={{
                            fontSize: width * 0.035,
                            color: "#666",
                            marginBottom: 5,
                          }}
                        >
                          목표 달성률:{" "}
                          {
                            accountInfo.savings_accounts[0]
                              .progress_percentage
                          }
                          %
                        </Text>
                        <View
                          style={{
                            height: 10,
                            backgroundColor: "#EEEEEE",
                            borderRadius: 5,
                            overflow: "hidden",
                          }}
                        >
                          <View
                            style={{
                              width: `${accountInfo.savings_accounts[0].progress_percentage}%`,
                              height: "100%",
                              backgroundColor: "#2D5BFF",
                            }}
                          />
                        </View>
                      </View>
                    </View>
                  ) : (
                    <ServiceTitleContainer>
                      <ServiceTextContainer width={width}>
                        <ServiceTitle
                          width={width}
                          style={{ marginBottom: 4 }}
                        >
                          <ColoredText style={{ fontWeight: "700" }}>
                            야금야금
                          </ColoredText>
                        </ServiceTitle>
                        <ServiceDescription width={width}>
                          지루했던 금융에
                          {"\n"}
                          야구의 재미를 더하다!
                        </ServiceDescription>
                      </ServiceTextContainer>
                      <ServiceIcon
                        source={require("../../assets/recommend.png")}
                        resizeMode="contain"
                        style={{
                          width: 170,
                          height: 170,
                          marginLeft: "auto",
                          marginRight: -10,
                        }}
                      />
                    </ServiceTitleContainer>
                  )}
                  </AnimatedServiceCard>
                </RecommendSection>
                {isLoggedIn && (
                  <TouchableOpacity 
                    style={{ 
                    backgroundColor: "#2D5BFF",
                      padding: width * 0.03,
                      borderRadius: width * 0.02,
                    marginTop: width * 0.03,
                    }}
                    onPress={() => {
                    navigation.navigate("Service");
                    }}
                  >
                    <ButtonLabel width={width} style={{ color: "#FFFFFF" }}>
                      서비스 보기
                    </ButtonLabel>
                  </TouchableOpacity>
                )}
              </Container>
            </AnimatedScrollView>
        </MobileContainer>
      </AppWrapper>
    </>
  );
};

export default HomeScreen; 
