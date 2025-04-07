import React, { useState, useRef, useEffect } from "react";
import {
  useWindowDimensions,
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  Text,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import { useTeam } from "../context/TeamContext";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { BottomTabNavigationProp, BottomTabScreenProps } from "@react-navigation/bottom-tabs";
import { RootStackParamList } from "../navigation/AppNavigator";
import { useNavigation } from "@react-navigation/native";
import Carousel from "react-native-reanimated-carousel";
import { Ionicons } from "@expo/vector-icons";
import { api } from "../api/axios";
import { useAccountStore } from "../store/useStore";
import { SavingsAccount } from "../types/account";
import { teamColors, teamIdToCode, teamNameToCode } from "../styles/teamColors";

// SavingsAccount를 확장하여 필요한 필드 추가
interface ExtendedSavingsAccount extends SavingsAccount {
  team_id?: number;
}

// 규칙 인터페이스 정의
interface Rule {
  rule_id: number;
  rule_type: string;
  rule_name: string;
  rule_amount: number;
  is_active: boolean;
}

type MainPageNavigationProp = NativeStackNavigationProp<RootStackParamList>;
type TabNavigationProp = BottomTabNavigationProp<{
  홈: undefined;
  적금내역: { viewMode?: string };
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

// 규칙 아이템 타입 정의
interface RuleItem {
  id: number;
  title: string;
  rules: string[];
}

const MainPage = () => {
  const tabNavigation = useNavigation<TabNavigationProp>();
  const stackNavigation = useNavigation<MainPageNavigationProp>();
  const { teamColor, teamName, teamId, setTeamData } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const { accountInfo, isLoading: accountLoading, error: accountError, fetchAccountInfo } = useAccountStore();
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
  const [savingRules, setSavingRules] = useState<RuleItem[]>([]);

  // 계좌 정보 조회 - useAccountStore 사용
  useEffect(() => {
    fetchAccountInfo();
  }, []);

  // 팀 정보 설정 함수
  const setupTeamInfo = (account: ExtendedSavingsAccount) => {
    // 이미 TeamContext에 유효한 팀 정보가 있는지 확인
    // teamId가 0이 아니면 이미 팀 정보가 설정된 것으로 간주
    if (teamId !== 0) {
      console.log("이미 TeamContext에 팀 정보가 설정되어 있습니다:", { teamId, teamName });
      return;
    }
    
    // 기존 팀 정보가 없는 경우에만 계좌 정보를 기반으로 설정
    console.log("팀 정보 설정 시작", account);
    
    try {
      // 한화 이글스를 기본 팀으로 설정
      let teamCodeKey: keyof typeof teamColors = 'Hanwha';
      
      // 팀 이름으로 팀 코드 찾기
      if (account.team_name && account.team_name in teamNameToCode) {
        const foundCode = teamNameToCode[account.team_name];
        if (foundCode) {
          teamCodeKey = foundCode;
        }
      }
      
      // 팀 ID로 팀 코드 찾기
      if (teamCodeKey === 'Hanwha' && account.team_id && account.team_id in teamIdToCode) {
        const foundCode = teamIdToCode[account.team_id];
        if (foundCode) {
          teamCodeKey = foundCode;
        }
      }
      
      console.log("찾은 팀 코드:", teamCodeKey);
      console.log("팀 색상:", teamColors[teamCodeKey]);
      
      // 팀 데이터 구성
      const teamData = {
        team_id: account.team_id || 8, // 한화 이글스의 ID는 8
        team_name: account.team_name || '한화 이글스',
        team_color: teamColors[teamCodeKey].primary,
        team_color_secondary: teamColors[teamCodeKey].secondary,
        team_color_background: teamColors[teamCodeKey].background,
      };
      
      console.log("설정할 팀 데이터:", teamData);
      
      // TeamContext 업데이트
      setTeamData(teamData);
      
      return teamColors[teamCodeKey];
    } catch (error) {
      console.error("팀 정보 설정 중 오류 발생:", error);
      
      // 오류 발생 시 기본값 사용 (TeamContext에 설정이 없는 경우에만)
      if (teamId === 0) {
        const defaultTeamData = {
          team_id: 8,
          team_name: '한화 이글스',
          team_color: '#FF6600',
          team_color_secondary: '#003057',
          team_color_background: '#ffffff',
        };
        
        setTeamData(defaultTeamData);
      }
      return null;
    }
  };

  // 규칙 데이터 가져오기 (실제 API로 대체 필요)
  const fetchRules = async (accountId: string) => {
    try {
      // 실제 API 호출로 대체 필요
      // const response = await api.get(`/api/account/${accountId}/rules`);
      // return response.data;
      
      // 임시 데이터
      return [
        { rule_id: 1, rule_type: "basic", rule_name: "팀이 승리하는 경우", rule_amount: 3000, is_active: true },
        { rule_id: 2, rule_type: "basic", rule_name: "팀이 안타를 친 경우", rule_amount: 1000, is_active: true },
        { rule_id: 3, rule_type: "basic", rule_name: "팀이 홈런을 친 경우", rule_amount: 5000, is_active: true },
        { rule_id: 4, rule_type: "pitcher", rule_name: "투수 삼진을 잡는 경우", rule_amount: 1000, is_active: true },
        { rule_id: 5, rule_type: "pitcher", rule_name: "투수 볼넷을 던진 경우", rule_amount: -500, is_active: true },
        { rule_id: 6, rule_type: "pitcher", rule_name: "투수 자책점", rule_amount: -1000, is_active: true },
        { rule_id: 7, rule_type: "batter", rule_name: "타자 안타를 친 경우", rule_amount: 1000, is_active: true },
        { rule_id: 8, rule_type: "batter", rule_name: "타자 홈런을 친 경우", rule_amount: 5000, is_active: true },
        { rule_id: 9, rule_type: "batter", rule_name: "타자 도루하는 경우", rule_amount: 2000, is_active: true },
        { rule_id: 10, rule_type: "opponent", rule_name: "상대팀 삼진", rule_amount: 500, is_active: true },
        { rule_id: 11, rule_type: "opponent", rule_name: "상대팀 병살타", rule_amount: 1000, is_active: true },
        { rule_id: 12, rule_type: "opponent", rule_name: "상대팀 실책", rule_amount: 1000, is_active: true },
      ];
    } catch (err) {
      console.error("규칙 조회 실패:", err);
      return [];
    }
  };

  // 규칙을 타입별로 분류하는 함수
  const organizeRulesByType = (rules: Rule[]) => {
    const rulesByType: Record<string, Rule[]> = {
      basic: [],
      pitcher: [],
      batter: [],
      opponent: [],
    };
    
    rules.forEach(rule => {
      if (rule.rule_type in rulesByType) {
        rulesByType[rule.rule_type].push(rule);
      }
    });
    
    const organizedRules: RuleItem[] = [
      {
        id: 1,
        title: "기본 규칙",
        rules: rulesByType.basic.map(r => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`),
      },
      {
        id: 2,
        title: "투수 규칙",
        rules: rulesByType.pitcher.map(r => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`),
      },
      {
        id: 3,
        title: "타자 규칙",
        rules: rulesByType.batter.map(r => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`),
      },
      {
        id: 4,
        title: "상대팀 규칙",
        rules: rulesByType.opponent.map(r => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`),
      }
    ];
    
    return organizedRules;
  };

  // accountInfo가 변경될 때 실행
  useEffect(() => {
    const updateAccountData = async () => {
      if (accountInfo?.savings_accounts && accountInfo.savings_accounts.length > 0) {
        const account = accountInfo.savings_accounts[0] as ExtendedSavingsAccount;
        
        // 팀 정보 설정
        setupTeamInfo(account);
        
        // 계좌 데이터 설정
        setTargetAmount(account.saving_goal || 0);
        setCurrentAmount(account.total_amount || 0);
        setInterestRate(account.interest_rate || 2.5);
        
        // 추가 금리 계산 (기본 금리 기준)
        const baseRate = 2.5; // 기본 금리
        const additional = account.interest_rate - baseRate;
        setAdditionalRate(additional > 0 ? additional : 0);
        
        // 목표 제목 설정 (간단한 예시)
        setSavingTitle(`${account.team_name || teamName} 적금`);
        
        // 규칙 데이터 가져오기
        const rulesData = await fetchRules(account.account_id);
        const organizedRules = organizeRulesByType(rulesData);
        setSavingRules(organizedRules);
        
        setIsLoading(false);
      } else {
        // 계좌 정보가 없는 경우 기본값 설정
        setIsLoading(false);
        // 기본 규칙 데이터 설정
        setSavingRules([
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
          }
        ]);
      }
    };
    
    updateAccountData();
  }, [accountInfo]);

  const percentage = Math.min(
    100,
    Math.round((currentAmount / (targetAmount || 1)) * 100) // 0으로 나누기 방지
  );

  const formatAmount = (amount: number) => {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // 캐러셀 아이템 렌더링 함수
  const renderRuleItem = ({ item }: { item: RuleItem }) => {
    return (
      <RuleCarouselCard width={width}>
        <RuleCardHeader width={width} teamColor={teamColor.primary}>
          <RuleCardTitle width={width}>{item.title}</RuleCardTitle>
          <Ionicons name="information-circle-outline" size={20} color="white" />
        </RuleCardHeader>
        <RuleCardContent width={width}>
          {item.rules.map((rule: string, index: number) => (
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
          data={savingRules}
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
          {savingRules.map((_, index) => (
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
            야금야금 - {accountInfo?.savings_accounts?.[0]?.team_name || teamName || "팀 정보가 불러와지지 않았습니다."}
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
            {isLoading || accountLoading ? (
              <View style={{ padding: 20, alignItems: "center", justifyContent: "center" }}>
                <Text style={{ fontSize: 16, color: "#666" }}>데이터를 불러오는 중입니다...</Text>
              </View>
            ) : error || accountError ? (
              <View style={{ padding: 20, alignItems: "center", justifyContent: "center" }}>
                <Text style={{ fontSize: 16, color: "#ff4444" }}>
                  데이터를 불러오는데 실패했습니다.
                </Text>
              </View>
            ) : (
              <>
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
                          tabNavigation.navigate('적금내역', { viewMode: "list" });
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
                          tabNavigation.navigate('적금내역', { viewMode: "calendar" });
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
              </>
            )}
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default MainPage;
