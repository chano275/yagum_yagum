import React, { useState, useRef, useEffect } from "react";
import {
  useWindowDimensions,
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import { useTeam } from "../context/TeamContext";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { BottomTabNavigationProp } from "@react-navigation/bottom-tabs";
import { RootStackParamList } from "../navigation/AppNavigator";
import { useNavigation } from "@react-navigation/native";
import Carousel from "react-native-reanimated-carousel";
import { Ionicons } from "@expo/vector-icons";
import { api } from "../api/axios";

type MainPageNavigationProp = NativeStackNavigationProp<RootStackParamList>;
type TabNavigationProp = BottomTabNavigationProp<{
  홈: undefined;
  적금내역: undefined;
  리포트: undefined;
  혜택: undefined;
}>;

interface StyledProps {
  width: number;
}

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

const Header = styled.View<StyledProps & { teamColor: string }>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background-color: ${(props) => props.teamColor};
  padding: ${({ width }) => width * 0.04}px;
  padding-top: ${({ width }) => width * 0.1}px;
`;

const HeaderTitle = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.046}px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BellIcon = styled.Image`
  width: 24px;
  height: 24px;
`;

const ProgressSection = styled.View<StyledProps & { teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  padding: ${({ width }) => width * 0.04}px;
  padding-top: ${({ width }) => width * 0.02}px;
`;

const ProgressTitle = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.04}px;
  font-family: ${({ theme }) => theme.fonts.medium};
`;

const ProgressAmount = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.035}px;
  margin-vertical: ${({ width }) => width * 0.02}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ProgressBarContainer = styled.View<StyledProps>`
  height: ${({ width }) => width * 0.02}px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: ${({ width }) => width * 0.01}px;
  overflow: hidden;
`;

const ProgressFill = styled.View<{ percentage: number }>`
  height: 100%;
  width: ${(props) => `${props.percentage}%`};
  background-color: #ffffff;
  border-radius: 4px;
`;

const ProgressPercent = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.03}px;
  text-align: right;
  margin-top: ${({ width }) => width * 0.01}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const StatsRow = styled.View<StyledProps>`
  flex-direction: row;
  justify-content: space-between;
  padding: ${({ width }) => width * 0.04}px;
  background-color: white;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
`;

const StatText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const StatHighlight = styled.Text`
  color: #4caf50;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const CardsContainer = styled.ScrollView<StyledProps>`
  flex: 1;
  padding: ${({ width }) => width * 0.04}px;
`;

const Card = styled.View<StyledProps>`
  background-color: white;
  border-radius: ${({ width }) => width * 0.02}px;
  margin-bottom: ${({ width }) => width * 0.04}px;
  overflow: hidden;
  border-width: 1px;
  border-color: #eeeeee;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.08);
  `}
`;

const CardHeader = styled.View<StyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: ${({ width }) => width * 0.03}px;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
`;

const CardTitle = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.04}px;
  font-weight: bold;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ViewAllLink = styled.Text<StyledProps & { teamColor: string }>`
  font-size: ${({ width }) => width * 0.03}px;
  color: ${(props) => props.teamColor};
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const CardContent = styled.View<StyledProps>`
  padding: ${({ width }) => width * 0.03}px;
`;

const CardText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  line-height: ${({ width }) => width * 0.05}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RedText = styled.Text<{ teamColor: string }>`
  color: ${(props) => props.teamColor};
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RuleText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  margin-bottom: ${({ width }) => width * 0.01}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const HistoryItem = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.02}px;
`;

const TeamLogo = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.06}px;
  height: ${({ width }) => width * 0.06}px;
  margin-right: ${({ width }) => width * 0.02}px;
`;

const HistoryText = styled.Text<StyledProps>`
  flex: 1;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const HistoryAmount = styled.Text<StyledProps & { teamColor: string }>`
  font-size: ${({ width }) => width * 0.035}px;
  color: ${(props) => props.teamColor};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ScheduleItem = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.02}px;
`;

const ScheduleDate = styled.Text<StyledProps>`
  width: ${({ width }) => width * 0.1}px;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ScheduleTeam = styled.Text<StyledProps>`
  flex: 1;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ScheduleTime = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

// 캐러셀 관련 새로운 스타일 컴포넌트
const RuleCarouselCard = styled.View<StyledProps>`
  background-color: white;
  border-radius: ${({ width }) => width * 0.02}px;
  overflow: hidden;
  margin: 0 5px;
  height: ${({ width }) => width * 0.4}px;
  border-width: 1px;
  border-color: #eeeeee;
`;

const RuleCardHeader = styled.View<StyledProps & { teamColor: string }>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: ${({ width }) => width * 0.03}px;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
  background-color: ${(props) => props.teamColor};
`;

const RuleCardTitle = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.04}px;
  font-weight: bold;
  color: white;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const RuleCardContent = styled.View<StyledProps>`
  padding: ${({ width }) => width * 0.03}px;
  flex: 1;
`;

const PaginationContainer = styled.View`
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
`;

const PaginationDot = styled.View<{ active: boolean; teamColor: string }>`
  width: 8px;
  height: 8px;
  border-radius: 4px;
  margin: 0 4px;
  background-color: ${(props) => (props.active ? props.teamColor : "#CCCCCC")};
`;

const MainPage = () => {
  const navigation = useNavigation<MainPageNavigationProp>();
  const { teamColor, teamName } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 상태값 업데이트
  const [currentAmount, setCurrentAmount] = useState(0);
  const [targetAmount, setTargetAmount] = useState(0);
  const [savingTitle, setSavingTitle] = useState("목표 저축");
  const [interestRate, setInterestRate] = useState(0);
  const [additionalRate, setAdditionalRate] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSlide, setActiveSlide] = useState(0);

  // 계좌 정보 조회
  useEffect(() => {
    const fetchAccountData = async () => {
      try {
        setIsLoading(true);
        const accountId = 1; // 실제 구현에서는 저장된 계정 ID 사용

        const response = await api.get(`/api/account/${accountId}`);

        if (response.status === 200) {
          const accountData = response.data;

          // API 응답에서 목표 금액과 현재 금액 설정
          setTargetAmount(accountData.SAVING_GOAL || 0);
          setCurrentAmount(accountData.TOTAL_AMOUNT || 0);

          // 금리 정보 설정
          const baseRate = 2.5; // 기본 금리
          const rate = accountData.INTEREST_RATE || baseRate;
          setInterestRate(rate);

          // 추가 금리 계산 (기본 금리 기준)
          const additional = rate - baseRate;
          setAdditionalRate(additional);

          // 목표 제목 설정
          setSavingTitle("유니폼 구매(목표 금액에 따라 하드코딩)");
        }
      } catch (err) {
        console.error("계좌 정보 조회 실패:", err);
        setError(err);
        // 에러 발생시 기본값 설정
        setTargetAmount(500000);
        setCurrentAmount(300000);
        setInterestRate(2.5);
        setAdditionalRate(0);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAccountData();
  }, []);

  const percentage = Math.min(
    100,
    Math.round((currentAmount / (targetAmount || 1)) * 100) // 0으로 나누기 방지
  );

  const formatAmount = (amount: number) => {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // 적금 규칙 데이터
  const ruleData = [
    {
      id: 1,
      title: "기본 규칙",
      rules: [
        "팀이 승리하는 경우: 3,000원",
        "팀이 안타를 친 경우: 1,000원",
        "팀이 홈런을 친 경우: 5,000원",
      ],
    },
    {
      id: 2,
      title: "투수 규칙",
      rules: [
        "투수 삼진을 잡는 경우: 1,000원",
        "투수 볼넷을 던진 경우: -500원",
        "투수 자책점: -1,000원",
      ],
    },
    {
      id: 3,
      title: "타자 규칙",
      rules: [
        "타자 안타를 친 경우: 1,000원",
        "타자 홈런을 친 경우: 5,000원",
        "타자 도루하는 경우: 2,000원",
      ],
    },
    {
      id: 4,
      title: "상대팀 규칙",
      rules: [
        "상대팀 삼진: 500원",
        "상대팀 병살타: 1,000원",
        "상대팀 실책: 1,000원",
      ],
    },
  ];

  // 캐러셀 아이템 렌더링 함수
  const renderRuleItem = ({ item }) => {
    return (
      <RuleCarouselCard width={width}>
        <RuleCardHeader width={width} teamColor={teamColor.primary}>
          <RuleCardTitle width={width}>{item.title}</RuleCardTitle>
          <Ionicons name="information-circle-outline" size={20} color="white" />
        </RuleCardHeader>
        <RuleCardContent width={width}>
          {item.rules.map((rule, index) => (
            <RuleText key={index} width={width}>
              • {rule}
            </RuleText>
          ))}
        </RuleCardContent>
      </RuleCarouselCard>
    );
  };

  // 캐러셀 컴포넌트
  const RulesCarousel = () => {
    return (
      <View>
        <Carousel
          loop
          width={width - width * 0.12}
          height={width * 0.4}
          data={ruleData}
          scrollAnimationDuration={1000}
          onSnapToItem={(index) => setActiveSlide(index)}
          renderItem={renderRuleItem}
          mode="parallax"
          modeConfig={{
            parallaxScrollingScale: 0.95,
            parallaxScrollingOffset: 30,
          }}
        />
        <PaginationContainer>
          {ruleData.map((_, index) => (
            <PaginationDot
              key={index}
              active={activeSlide === index}
              teamColor={teamColor.primary}
            />
          ))}
        </PaginationContainer>
      </View>
    );
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <HeaderTitle width={width}>
            야금야금 - {teamName || "팀 정보가 불러와지지 않았습니다."}
          </HeaderTitle>
          <TouchableOpacity>
            <BellIcon source={require("../../assets/icon.png")} />
          </TouchableOpacity>
        </Header>

        <SafeAreaView style={{ flex: 1, paddingBottom: 60 }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: 20 }}
          >
            <ProgressSection width={width} teamColor={teamColor.primary}>
              <ProgressTitle width={width}>{savingTitle}</ProgressTitle>
              <ProgressAmount width={width}>
                {formatAmount(currentAmount)}원 / {formatAmount(targetAmount)}원
              </ProgressAmount>
              <ProgressBarContainer width={width}>
                <ProgressFill percentage={percentage} />
              </ProgressBarContainer>
              <ProgressPercent width={width}>
                {percentage}% 달성
              </ProgressPercent>
            </ProgressSection>

            <StatsRow width={width}>
              <StatText width={width}>
                현재 금리: {interestRate.toFixed(1)}%
                {additionalRate > 0 && (
                  <StatHighlight> +{additionalRate.toFixed(1)}%</StatHighlight>
                )}
              </StatText>
              <StatText width={width}>
                팀 순위: 3위(API) <StatHighlight>+2</StatHighlight>
              </StatText>
            </StatsRow>

            <View style={{ padding: width * 0.04 }}>
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>
                    오늘의 적금 비교 (API 연결 필요)
                  </CardTitle>
                </CardHeader>
                <CardContent width={width}>
                  <CardText width={width}>
                    <RedText teamColor={teamColor.primary}>↗</RedText> 두산이
                    승리했지만, 우리팀의 적금이 2배 더 많네요!
                  </CardText>
                </CardContent>
              </Card>

              {/* 적금 규칙 캐러셀 카드 */}
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>적금 규칙 (API 연결 필요)</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                  <RulesCarousel />
                </CardContent>
              </Card>

              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>
                    최근 적금 내역 (API 연결 필요)
                  </CardTitle>
                  <TouchableOpacity
                    onPress={() => {
                      navigation.navigate("Main", {
                        screen: "적금내역",
                        params: { viewMode: "list" },
                      });
                    }}
                  >
                    <ViewAllLink width={width} teamColor={teamColor.primary}>
                      전체 내역 &gt;
                    </ViewAllLink>
                  </TouchableOpacity>
                </CardHeader>
                <CardContent width={width}>
                  <HistoryItem width={width}>
                    <TeamLogo
                      width={width}
                      source={require("../../assets/icon.png")}
                    />
                    <HistoryText width={width}>3/11 승리</HistoryText>
                    <HistoryAmount width={width} teamColor={teamColor.primary}>
                      +15,000원
                    </HistoryAmount>
                  </HistoryItem>
                  <HistoryItem width={width}>
                    <TeamLogo
                      width={width}
                      source={require("../../assets/icon.png")}
                    />
                    <HistoryText width={width}>3/9 안타 7개</HistoryText>
                    <HistoryAmount width={width} teamColor={teamColor.primary}>
                      +7,000원
                    </HistoryAmount>
                  </HistoryItem>
                  <HistoryItem width={width}>
                    <TeamLogo
                      width={width}
                      source={require("../../assets/icon.png")}
                    />
                    <HistoryText width={width}>
                      3/8 승리, 안타 9개, 홈런 1개
                    </HistoryText>
                    <HistoryAmount width={width} teamColor={teamColor.primary}>
                      +12,000원
                    </HistoryAmount>
                  </HistoryItem>
                </CardContent>
              </Card>

              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>
                    다음 경기 일정 (API 연결 필요)
                  </CardTitle>
                  <TouchableOpacity
                    onPress={() => {
                      navigation.navigate("Main", {
                        screen: "적금내역",
                        params: { viewMode: "calendar" },
                      });
                    }}
                  >
                    <ViewAllLink width={width} teamColor={teamColor.primary}>
                      전체 일정 &gt;
                    </ViewAllLink>
                  </TouchableOpacity>
                </CardHeader>
                <CardContent width={width}>
                  <ScheduleItem width={width}>
                    <ScheduleDate width={width}>3/22</ScheduleDate>
                    <ScheduleTeam width={width}>vs NC 다이노스</ScheduleTeam>
                    <ScheduleTime width={width}>14:00 광주</ScheduleTime>
                  </ScheduleItem>
                  <ScheduleItem width={width}>
                    <ScheduleDate width={width}>3/23</ScheduleDate>
                    <ScheduleTeam width={width}>vs NC 다이노스</ScheduleTeam>
                    <ScheduleTime width={width}>14:00 광주</ScheduleTime>
                  </ScheduleItem>
                  <ScheduleItem width={width}>
                    <ScheduleDate width={width}>3/25</ScheduleDate>
                    <ScheduleTeam width={width}>vs LG 트윈스</ScheduleTeam>
                    <ScheduleTime width={width}>18:30 광주</ScheduleTime>
                  </ScheduleItem>
                </CardContent>
              </Card>
            </View>
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default MainPage;
