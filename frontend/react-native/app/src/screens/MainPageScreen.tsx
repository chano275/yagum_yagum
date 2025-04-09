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
import {
  BottomTabNavigationProp,
  BottomTabScreenProps,
} from "@react-navigation/bottom-tabs";
import { RootStackParamList } from "../navigation/AppNavigator";
import { useNavigation } from "@react-navigation/native";
import Carousel from "react-native-reanimated-carousel";
import { Ionicons } from "@expo/vector-icons";
import { api } from "../api/axios";
import { useAccountStore } from "../store/useStore";
import { SavingsAccount } from "../types/account";
import { teamColors, teamIdToCode } from "../styles/teamColors";
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// 경기 일정 데이터 타입 정의
interface GameSchedule {
  DATE: string;
  HOME_TEAM_ID: number;
  AWAY_TEAM_ID: number;
  GAME_SCHEDULE_KEY: number;
  home_team_name: string;
  away_team_name: string;
}

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

interface BaseStyledProps {
  width: number;
}

interface StyledProps extends BaseStyledProps {
  insetsTop?: number;
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
  padding-top: ${props => props.insetsTop || 0}px;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
  `}
`;

const Header = styled.View<BaseStyledProps & { teamColor: string }>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background-color: ${(props) => props.teamColor};
  padding: ${({ width }) => width * 0.04}px;
  padding-top: ${({ width }) => width * 0.1}px;
  position: relative;
`;

const HeaderTitle = styled.Text<BaseStyledProps>`
  position: absolute;
  left: 0;
  right: 0;
  top: ${({ width }) => width * 0.1}px;
  color: white;
  font-size: ${({ width }) => width * 0.046}px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
  text-align: center;
`;

const BackButton = styled.TouchableOpacity`
  padding: 8px;
  width: 40px;
  height: 40px;
  justify-content: center;
  align-items: flex-start;
`;

const IconContainer = styled.TouchableOpacity`
  padding: 8px;
  width: 40px;
  height: 40px;
  justify-content: center;
  align-items: flex-end;
`;

const BellIcon = styled.Image`
  width: 24px;
  height: 24px;
`;

const ProgressSection = styled.View<BaseStyledProps & { teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  padding: ${({ width }) => width * 0.04}px;
  padding-top: ${({ width }) => width * 0.02}px;
`;

const ProgressTitle = styled.Text<BaseStyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.04}px;
  font-family: ${({ theme }) => theme.fonts.medium};
`;

const ProgressAmount = styled.Text<BaseStyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.035}px;
  margin-vertical: ${({ width }) => width * 0.02}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ProgressBarContainer = styled.View<BaseStyledProps>`
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

const ProgressPercent = styled.Text<BaseStyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.03}px;
  text-align: right;
  margin-top: ${({ width }) => width * 0.01}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const StatsRow = styled.View<BaseStyledProps>`
  flex-direction: row;
  justify-content: space-between;
  padding: ${({ width }) => width * 0.04}px;
  background-color: white;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
`;

const StatText = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const StatHighlight = styled.Text`
  color: #4caf50;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const CardsContainer = styled.ScrollView<BaseStyledProps>`
  flex: 1;
  padding: ${({ width }) => width * 0.04}px;
`;

const Card = styled.View<BaseStyledProps>`
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

const CardHeader = styled.View<BaseStyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: ${({ width }) => width * 0.03}px;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
`;

const CardTitle = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.04}px;
  font-weight: bold;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ViewAllLink = styled.Text<BaseStyledProps & { teamColor: string }>`
  font-size: ${({ width }) => width * 0.03}px;
  color: ${(props) => props.teamColor};
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const CardContent = styled.View<BaseStyledProps>`
  padding: ${({ width }) => width * 0.03}px;
`;

const CardText = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  line-height: ${({ width }) => width * 0.05}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RedText = styled.Text<{ teamColor: string }>`
  color: ${(props) => props.teamColor};
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RuleText = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  margin-bottom: ${({ width }) => width * 0.01}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const HistoryItem = styled.View<BaseStyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.02}px;
`;

const TeamLogo = styled.Image<BaseStyledProps>`
  width: ${({ width }) => width * 0.06}px;
  height: ${({ width }) => width * 0.06}px;
  margin-right: ${({ width }) => width * 0.02}px;
`;

const HistoryText = styled.Text<BaseStyledProps>`
  flex: 1;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const HistoryAmount = styled.Text<BaseStyledProps & { teamColor: string }>`
  font-size: ${({ width }) => width * 0.035}px;
  color: ${(props) => props.teamColor};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ScheduleItem = styled.View<BaseStyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.02}px;
`;

const ScheduleDate = styled.Text<BaseStyledProps>`
  width: ${({ width }) => width * 0.1}px;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ScheduleTeam = styled.Text<BaseStyledProps>`
  flex: 1;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ScheduleTime = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

// 캐러셀 관련 새로운 스타일 컴포넌트
const RuleCarouselCard = styled.View<BaseStyledProps>`
  background-color: white;
  border-radius: ${({ width }) => width * 0.02}px;
  overflow: hidden;
  margin: 0 5px;
  height: ${({ width }) => width * 0.4}px;
  border-width: 1px;
  border-color: #eeeeee;
`;

const RuleCardHeader = styled.View<BaseStyledProps & { teamColor: string }>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: ${({ width }) => width * 0.03}px;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
  background-color: ${(props) => props.teamColor};
`;

const RuleCardTitle = styled.Text<BaseStyledProps>`
  font-size: ${({ width }) => width * 0.04}px;
  font-weight: bold;
  color: white;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const RuleCardDescription = styled.Text<BaseStyledProps>`
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
  const { width, height } = useWindowDimensions();
  const stackNavigation = useNavigation<MainPageNavigationProp>();
  const tabNavigation = useNavigation<TabNavigationProp>();
  const { teamName, teamColor, setTeamData } = useTeam();
  const {
    accountInfo,
    isLoading: accountLoading,
    error: accountError,
    fetchAccountInfo,
  } = useAccountStore();
  const insets = useSafeAreaInsets();

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
  const [teamRank, setTeamRank] = useState<number | null>(null);
  const [isRankLoading, setIsRankLoading] = useState<boolean>(true);

  // 경기 일정 관련 상태 추가
  const [gameSchedules, setGameSchedules] = useState<GameSchedule[]>([]);
  const [isScheduleLoading, setIsScheduleLoading] = useState<boolean>(true);
  const [scheduleError, setScheduleError] = useState<Error | null>(null);

  // 계좌 정보 조회 - useAccountStore 사용
  useEffect(() => {
    fetchAccountInfo();
  }, []);

  // 팀 ID 가져오기 함수
  const getTeamIdByName = (name: string): number => {
    const teamMapping: { [key: string]: number } = {
      "KIA 타이거즈": 1,
      "삼성 라이온즈": 2,
      "LG 트윈스": 3,
      "두산 베어스": 4,
      "KT 위즈": 5,
      "SSG 랜더스": 6,
      "롯데 자이언츠": 7,
      "한화 이글스": 8,
      "NC 다이노스": 9,
      "키움 히어로즈": 10,
    };
    return teamMapping[name] || 1;
  };

  // 팀 홈구장 도시 정보 함수
  const getTeamHomeCity = (teamId: number): string => {
    const cityMap: { [key: number]: string } = {
      1: "광주", // KIA 타이거즈
      2: "대구", // 삼성 라이온즈
      3: "서울", // LG 트윈스
      4: "서울", // 두산 베어스
      5: "수원", // KT 위즈
      6: "인천", // SSG 랜더스
      7: "부산", // 롯데 자이언츠
      8: "대전", // 한화 이글스
      9: "창원", // NC 다이노스
      10: "서울", // 키움 히어로즈
    };
    return cityMap[teamId] || "미정";
  };

  // 팀 정보 설정 함수 (무효화)
  const setupTeamInfo = (account: ExtendedSavingsAccount) => {
    // 팀 정보를 변경하지 않고 현재 값만 로그로 출력
    console.log("[MainPageScreen] 현재 팀 정보:", {
      teamId: account.team_id,
      teamName: account.team_name,
      teamColor: teamColor.primary,
    });

    if (account) {
      console.log("[MainPageScreen] 계좌 정보:", {
        accountTeamId: account.team_id,
        accountTeamName: account.team_name,
      });
    }

    // 값을 변경하지 않음
    return null;
  };

  // 경기 일정 조회
  useEffect(() => {
    const fetchGameSchedules = async () => {
      if (!teamName) return; // teamName이 없으면 실행 중단

      try {
        setIsScheduleLoading(true);

        // 팀명으로 팀 ID 가져오기
        const teamId = getTeamIdByName(teamName); // 이제 teamName은 string 타입이 보장됨

        // API 호출
        const response = await api.get(`/api/game/schedule/team/${teamId}`);

        if (response.status === 200 && Array.isArray(response.data)) {
          // 오늘 이후의 경기만 필터링
          const today = new Date();
          today.setHours(0, 0, 0, 0);

          const filteredGames = response.data
            .filter((game: GameSchedule) => {
              const gameDate = new Date(game.DATE);
              return gameDate >= today;
            })
            .sort((a: GameSchedule, b: GameSchedule) => {
              return new Date(a.DATE).getTime() - new Date(b.DATE).getTime();
            })
            .slice(0, 3); // 다음 3개 경기만 선택

          setGameSchedules(filteredGames);
        } else {
          throw new Error("API 응답 형식이 올바르지 않습니다");
        }
      } catch (err) {
        console.error("경기 일정 조회 실패:", err);
        setScheduleError(
          err instanceof Error ? err : new Error("알 수 없는 오류")
        );
        setGameSchedules([]);
      } finally {
        setIsScheduleLoading(false);
      }
    };

    fetchGameSchedules();
  }, [teamName]);

  // 팀 순위 정보를 가져오는 useEffect 추가
  useEffect(() => {
    const fetchTeamRank = async () => {
      try {
        setIsRankLoading(true);
        const response = await api.get("/api/game/team/ranking");

        if (response.status === 200 && Array.isArray(response.data)) {
          // 현재 사용자의 팀을 찾습니다
          const currentTeam = response.data.find(
            (team) => team.TEAM_NAME === teamName
          );

          if (currentTeam) {
            setTeamRank(currentTeam.RANK);
          }
        } else {
          console.error("팀 순위 API 응답 형식이, 예상과 다릅니다.");
        }
      } catch (err) {
        console.error("팀 순위 조회 실패:", err);
      } finally {
        setIsRankLoading(false);
      }
    };

    if (teamName) {
      fetchTeamRank();
    }
  }, [teamName]);

  // 규칙 데이터 가져오기 (실제 API로 대체 필요)
  const fetchRules = async (accountId: string) => {
    try {
      // 실제 API 호출로 대체 필요
      // const response = await api.get(`/api/account/${accountId}/rules`);
      // return response.data;

      // 임시 데이터
      return [
        {
          rule_id: 1,
          rule_type: "basic",
          rule_name: "팀이 승리하는 경우",
          rule_amount: 3000,
          is_active: true,
        },
        {
          rule_id: 2,
          rule_type: "basic",
          rule_name: "팀이 안타를 친 경우",
          rule_amount: 1000,
          is_active: true,
        },
        {
          rule_id: 3,
          rule_type: "basic",
          rule_name: "팀이 홈런을 친 경우",
          rule_amount: 5000,
          is_active: true,
        },
        {
          rule_id: 4,
          rule_type: "pitcher",
          rule_name: "투수 삼진을 잡는 경우",
          rule_amount: 1000,
          is_active: true,
        },
        {
          rule_id: 5,
          rule_type: "pitcher",
          rule_name: "투수 볼넷을 던진 경우",
          rule_amount: -500,
          is_active: true,
        },
        {
          rule_id: 6,
          rule_type: "pitcher",
          rule_name: "투수 자책점",
          rule_amount: -1000,
          is_active: true,
        },
        {
          rule_id: 7,
          rule_type: "batter",
          rule_name: "타자 안타를 친 경우",
          rule_amount: 1000,
          is_active: true,
        },
        {
          rule_id: 8,
          rule_type: "batter",
          rule_name: "타자 홈런을 친 경우",
          rule_amount: 5000,
          is_active: true,
        },
        {
          rule_id: 9,
          rule_type: "batter",
          rule_name: "타자 도루하는 경우",
          rule_amount: 2000,
          is_active: true,
        },
        {
          rule_id: 10,
          rule_type: "opponent",
          rule_name: "상대팀 삼진",
          rule_amount: 500,
          is_active: true,
        },
        {
          rule_id: 11,
          rule_type: "opponent",
          rule_name: "상대팀 병살타",
          rule_amount: 1000,
          is_active: true,
        },
        {
          rule_id: 12,
          rule_type: "opponent",
          rule_name: "상대팀 실책",
          rule_amount: 1000,
          is_active: true,
        },
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

    rules.forEach((rule) => {
      if (rule.rule_type in rulesByType) {
        rulesByType[rule.rule_type].push(rule);
      }
    });

    const organizedRules: RuleItem[] = [
      {
        id: 1,
        title: "기본 규칙",
        rules: rulesByType.basic.map(
          (r) => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`
        ),
      },
      {
        id: 2,
        title: "투수 규칙",
        rules: rulesByType.pitcher.map(
          (r) => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`
        ),
      },
      {
        id: 3,
        title: "타자 규칙",
        rules: rulesByType.batter.map(
          (r) => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`
        ),
      },
      {
        id: 4,
        title: "상대팀 규칙",
        rules: rulesByType.opponent.map(
          (r) => `${r.rule_name}: ${r.rule_amount.toLocaleString()}원`
        ),
      },
    ];

    return organizedRules;
  };

  // accountInfo가 변경될 때 실행
  useEffect(() => {
    const updateAccountData = async () => {
      if (
        accountInfo?.savings_accounts &&
        accountInfo.savings_accounts.length > 0
      ) {
        const account = accountInfo
          .savings_accounts[0] as ExtendedSavingsAccount;

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
    },
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
        <RuleCardDescription width={width}>
          {item.rules.map((rule: string, index: number) => (
            <RuleText key={index} width={width}>
              • {rule}
            </RuleText>
          ))}
        </RuleCardDescription>
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
      <MobileContainer width={width} insetsTop={insets.top}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <BackButton onPress={() => stackNavigation.navigate("Home")}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </BackButton>
          <HeaderTitle width={width}>
            야금야금 -{" "}
            {accountInfo?.savings_accounts?.[0]?.team_name ||
              teamName ||
              "팀 정보가 불러와지지 않았습니다."}
          </HeaderTitle>
          <IconContainer>
            <BellIcon source={require("../../assets/icon.png")} />
          </IconContainer>
        </Header>

          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: insets.bottom + 20 }}
        >
          {isLoading || accountLoading ? (
            <View
              style={{
                padding: 20,
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Text style={{ fontSize: 16, color: "#666" }}>
                데이터를 불러오는 중입니다...
              </Text>
            </View>
          ) : error || accountError ? (
            <View
              style={{
                padding: 20,
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Text style={{ fontSize: 16, color: "#ff4444" }}>
                데이터를 불러오는데 실패했습니다.
              </Text>
            </View>
          ) : (
            <>
            <ProgressSection width={width} teamColor={teamColor.primary}>
              <ProgressTitle width={width}>{savingTitle}</ProgressTitle>
              <ProgressAmount width={width}>
                  {formatAmount(currentAmount)}원 /{" "}
                  {formatAmount(targetAmount)}원
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
                    <StatHighlight>
                      {" "}
                      +{additionalRate.toFixed(1)}%
                    </StatHighlight>
                )}
              </StatText>

              <StatText width={width}>
                  팀 순위:{" "}
                  {isRankLoading
                    ? "로딩 중..."
                    : teamRank
                    ? `${teamRank}위`
                    : "순위 없음"}{" "}
                  <StatHighlight>+2</StatHighlight>
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
                      <RedText teamColor={teamColor.primary}>↗</RedText>{" "}
                      두산이 승리했지만, 우리팀의 적금이 2배 더 많네요!
                  </CardText>
                </CardContent>
              </Card>

              {/* 적금 규칙 캐러셀 카드 */}
              <Card width={width}>
                <CardHeader width={width}>
                    <CardTitle width={width}>
                      적금 규칙 (API 연결 필요)
                    </CardTitle>
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
                        tabNavigation.navigate("적금내역", {
                          viewMode: "list",
                      });
                    }}
                  >
                      <ViewAllLink
                        width={width}
                        teamColor={teamColor.primary}
                      >
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
                      <HistoryAmount
                        width={width}
                        teamColor={teamColor.primary}
                      >
                      +15,000원
                    </HistoryAmount>
                  </HistoryItem>
                  <HistoryItem width={width}>
                    <TeamLogo
                      width={width}
                      source={require("../../assets/icon.png")}
                    />
                    <HistoryText width={width}>3/9 안타 7개</HistoryText>
                      <HistoryAmount
                        width={width}
                        teamColor={teamColor.primary}
                      >
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
                      <HistoryAmount
                        width={width}
                        teamColor={teamColor.primary}
                      >
                      +12,000원
                    </HistoryAmount>
                  </HistoryItem>
                </CardContent>
              </Card>

              <Card width={width}>
                <CardHeader width={width}>
                    <CardTitle width={width}>다음 경기 일정</CardTitle>
                  <TouchableOpacity
                    onPress={() => {
                        tabNavigation.navigate("적금내역", {
                          viewMode: "calendar",
                      });
                    }}
                  >
                      <ViewAllLink
                        width={width}
                        teamColor={teamColor.primary}
                      >
                      전체 일정 &gt;
                    </ViewAllLink>
                  </TouchableOpacity>
                </CardHeader>
                <CardContent width={width}>
                    {isScheduleLoading ? (
                      <View style={{ padding: 10, alignItems: "center" }}>
                        <Text>경기 일정 로딩 중...</Text>
                      </View>
                    ) : scheduleError ? (
                      <View style={{ padding: 10, alignItems: "center" }}>
                        <Text>경기 일정을 불러오는데 실패했습니다.</Text>
                      </View>
                    ) : gameSchedules.length > 0 ? (
                      gameSchedules.map((game) => {
                        if (!teamName) return null; // teamName 없으면 렌더링 안함

                        const isHomeGame =
                          game.HOME_TEAM_ID === getTeamIdByName(teamName); // 이제 teamName은 string
                        const opponentTeam = isHomeGame
                          ? game.away_team_name
                          : game.home_team_name;
                        const gameDate = new Date(game.DATE);
                        const month = gameDate.getMonth() + 1;
                        const day = gameDate.getDate();
                        const location = getTeamHomeCity(
                          isHomeGame ? game.HOME_TEAM_ID : game.AWAY_TEAM_ID
                        );

                        return (
                          <ScheduleItem
                            key={game.GAME_SCHEDULE_KEY}
                            width={width}
                          >
                            <ScheduleDate
                              width={width}
                            >{`${month}/${day}`}</ScheduleDate>
                            <ScheduleTeam
                              width={width}
                            >{`vs ${opponentTeam}`}</ScheduleTeam>
                            <ScheduleTime width={width}>
                              {location}{" "}
                              <Text>({isHomeGame ? "홈" : "원정"})</Text>
                            </ScheduleTime>
                  </ScheduleItem>
                        );
                      })
                    ) : (
                      <View style={{ padding: 10, alignItems: "center" }}>
                        <Text>표시할 경기 일정이 없습니다.</Text>
                      </View>
                    )}
                </CardContent>
              </Card>
            </View>
            </>
          )}
          </ScrollView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default MainPage;
