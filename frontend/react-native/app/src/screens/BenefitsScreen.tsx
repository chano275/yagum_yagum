import React from "react";
import {
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  useWindowDimensions,
  Alert,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import { Ionicons } from "@expo/vector-icons";
import { useTeam } from "@/context/TeamContext";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "@/navigation/AppNavigator";

// 네비게이션 타입 정의
type BenefitsScreenNavigationProp =
  NativeStackNavigationProp<RootStackParamList>;

// 동적 스타일링을 위한 인터페이스
interface StyledProps {
  width: number;
}

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

const AppWrapper = styled.View`
  flex: 1;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.background};
  width: 100%;
`;

const MobileContainer = styled.View<StyledProps>`
  width: ${({ width }) => {
    const isWeb = Platform.OS === "web";
    const deviceWidth = Math.min(width, MAX_MOBILE_WIDTH);
    return isWeb ? `${BASE_MOBILE_WIDTH}px` : `${deviceWidth}px`;
  }};
  max-width: 100%;
  flex: 1;
  align-self: center;
  overflow: hidden;
  position: relative;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
  `}
`;

// 팀 컬러를 적용하도록 Header 컴포넌트 수정
const Header = styled.View<{ teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  padding: 20px;
  padding-top: 60px;
  padding-bottom: 15px;
`;

const HeaderTitle = styled.Text`
  color: white;
  font-size: 18px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BenefitCard = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  background-color: white;
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 20px;
  border: 1px solid #f0f0f0;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.05);
  `}
`;

// 수정된 IconContainer 컴포넌트
const IconContainer = styled.View<{ bgColor: string }>`
  width: 40px;
  height: 40px;
  border-radius: 20px;
  background-color: ${(props) =>
    props.bgColor === "#ffffff" ? "#f0f0f0" : props.bgColor};
  border: ${(props) =>
    props.bgColor === "#ffffff" ? "1px solid #dddddd" : "none"};
  justify-content: center;
  align-items: center;
  margin-right: 15px;
`;

const BenefitContent = styled.View`
  flex: 1;
`;

const BenefitTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BenefitDescription = styled.Text`
  font-size: 14px;
  color: #666;
  line-height: 20px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const NavigationArrow = styled.View`
  margin-left: 10px;
`;

const BenefitsScreen = () => {
  // useTeam 훅을 사용해 팀 컬러 정보 가져오기
  const { teamColor } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 네비게이션 추가
  const navigation = useNavigation<BenefitsScreenNavigationProp>();

  // 혜택 데이터
  const benefits = [
    {
      id: "1",
      title: "우대금리 혜택",
      description:
        "적금 목표 달성 시 기본금리에 추가로 최대 1.0%p의 우대금리가 제공됩니다.",
      icon: "cash-outline",
      bgColor: teamColor.primary,
      onPress: () => {
        // 금리 혜택 상세 페이지로 이동
        navigation.navigate("Primerate", {
          benefitType: "interest",
          title: "우대금리 혜택",
        });
      },
    },
    {
      id: "2",
      title: "경기 직관 인증",
      description:
        "홈경기 직관 티켓 인증을 3번 완료하면 우대금리 0.1%p가 추가 제공됩니다.",
      icon: "ticket-outline",
      bgColor: "#FF5252",
      onPress: () => {
        // 티켓 인증 페이지로 이동
        navigation.navigate("Verifyticket", {
          benefitType: "ticket",
          title: "경기 직관 인증",
        });
      },
    },
    {
      id: "3",
      title: "팀 굿즈 할인",
      description:
        "응원팀 공식 굿즈 구매 시 최대 20% 할인 혜택을 받을 수 있습니다.",
      icon: "shirt-outline",
      bgColor: "#4CAF50",
      onPress: () => {
        // 굿즈 쇼핑 페이지로 이동
        navigation.navigate("Merchdiscount", {
          benefitType: "goods",
          title: "팀 굿즈 할인",
        });
      },
    },
    {
      id: "4",
      title: "팀 순위 맞추기",
      description:
        "시즌 종료 후 예측한 순위와 실제 순위가 일치하면 우대금리가 제공됩니다.",
      icon: "trophy-outline",
      bgColor: teamColor.secondary,
      onPress: () => {
        // 순위 예측 페이지로 이동
        navigation.navigate("Matchrank", {
          benefitType: "ranking",
          title: "팀 순위 맞추기",
        });
      },
    },
  ];

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        {/* 헤더에 팀 컬러 적용 */}
        <Header teamColor={teamColor.primary}>
          <HeaderTitle>혜택</HeaderTitle>
        </Header>

        <SafeAreaView style={{ flex: 1, backgroundColor: "#F5F5F5" }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ padding: 16 }}
          >
            {benefits.map((benefit) => (
              <TouchableOpacity
                key={benefit.id}
                onPress={benefit.onPress}
                activeOpacity={0.7}
              >
                <BenefitCard width={width}>
                  <IconContainer bgColor={benefit.bgColor}>
                    <Ionicons name={benefit.icon} size={24} color="white" />
                  </IconContainer>
                  <BenefitContent>
                    <BenefitTitle>{benefit.title}</BenefitTitle>
                    <BenefitDescription>
                      {benefit.description}
                    </BenefitDescription>
                  </BenefitContent>
                  <NavigationArrow>
                    <Ionicons
                      name="chevron-forward"
                      size={20}
                      color="#CCCCCC"
                    />
                  </NavigationArrow>
                </BenefitCard>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default BenefitsScreen;
