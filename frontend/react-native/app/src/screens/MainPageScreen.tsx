import React, { useState, useRef, useEffect } from "react";
import {
  useWindowDimensions,
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  Text,
  ActivityIndicator,
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
import { MaterialIcons } from "@expo/vector-icons";

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
  preferred_player_type?: number;
}

// 규칙 인터페이스 정의
interface Rule {
  rule_id: number;
  rule_type: string;
  rule_name: string;
  rule_amount: number;
  is_active: boolean;
}

// 간소화된 경기 상태 타입 추가
type GameStatus = "win" | "lose" | "draw" | "cancelled" | "upcoming";

// 거래 내역 아이템 타입
interface TransactionItem {
  id: string;
  opponent: string;
  date: string;
  description: string;
  amount: number;
  wins: number;
  result: string; // 승패 결과 텍스트 (승, 패, 무, 취소, 경기전)
  status: GameStatus; // 결과 상태 (win, lose, draw, cancelled, upcoming)
}

// 우대금리 정보 인터페이스 추가
interface InterestDetails {
  base_interest_rate: number;
  mission_interest_rate: number;
  total_interest_rate: number;
  total_mission_rate: number;
  mission_details: {
    mission_id: number;
    mission_name: string;
    mission_rate: number;
    current_count: number;
    max_count: number;
    is_completed: boolean;
  }[];
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
  height: 56px;
  padding-horizontal: 16px;
  padding-top: ${Platform.OS === 'web' ? '0px' : '${StatusBar.currentHeight}px'};
  position: relative;
`;

const HeaderTitle = styled.Text<StyledProps>`
  color: white;
  font-size: 20px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
  text-align: center;
  flex: 1;
`;

const BackButton = styled.TouchableOpacity`
  padding: 8px;
  width: 40px;
  height: 40px;
  justify-content: center;
  align-items: center;
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
const ProgressSection = styled.View<StyledProps & { teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  padding: ${({ width }) => width * 0.04}px;
  padding-top: ${({ width }) => width * 0.02}px;
`;
const ProgressTitleContainer = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.01}px;
`;
const ProgressTitleLogo = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.06}px;
  height: ${({ width }) => width * 0.06}px;
  margin-right: ${({ width }) => width * 0.02}px;
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

const StatHighlight = styled.Text<{ status?: "up" | "down" | "same" }>`
  color: ${(props) => {
    switch (props.status) {
      case "up":
        return "#4caf50"; // 초록색 (상승)
      case "down":
        return "#f44336"; // 빨간색 (하락)
      case "same":
        return "#9e9e9e"; // 회색 (유지)
      default:
        return "#4caf50"; // 기본값 (초록색)
    }
  }};
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
  padding: ${({ width }) => width * 0.01}px 0;
`;
const TeamLogo = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.06}px;
  height: ${({ width }) => width * 0.06}px;
  margin-horizontal: ${({ width }) => width * 0.015}px;
  resize-mode: contain;
`;
const HistoryDate = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #666;
  width: ${({ width }) => width * 0.08}px;
  margin-right: ${({ width }) => width * 0.0}px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;
const ResultText = styled.Text<StyledProps & { status: GameStatus }>`
  flex: 1;
  font-size: ${({ width }) => width * 0.035}px;
  color: ${({ status }) => {
    switch (status) {
      case 'win':
        return '#4caf50'; // 초록색 (승리)
      case 'lose':
        return '#f44336'; // 빨간색 (패배)
      case 'draw':
        return '#9e9e9e'; // 회색 (무승부)
      case 'cancelled':
        return '#6c757d'; // 어두운 회색 (취소)
      default:
        return '#333';    // 기본값 (경기전)
    }
  }};
  font-weight: ${({ status }) => status === 'win' ? 'bold' : 'normal'};
  font-family: ${({ theme }) => theme.fonts.regular};
  margin-left: ${({ width }) => width * 0.01}px;
`;
const HistoryAmount = styled.Text<StyledProps & { teamColor: string }>`
  font-size: ${({ width }) => width * 0.035}px;
  color: ${(props) => props.teamColor};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ScheduleItem = styled.TouchableOpacity<StyledProps>`
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-bottom: ${({ width }) => width * 0.03}px;
  margin-top: ${({ width }) => width * 0.01}px;
  padding: ${({ width }) => width * 0.015}px 0;
`;
const ScheduleDate = styled.Text<StyledProps>`
  width: ${({ width }) => width * 0.1}px;
  font-size: ${({ width }) => width * 0.035}px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

// vs 텍스트 추가
const VsText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.03}px;
  color: #666;
  margin-right: ${({ width }) => width * 0.01}px;
`;

// 팀 로고 컨테이너
const TeamContainer = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding-horizontal: ${({ width }) => width * 0.01}px;
`;

// 팀 로고 이미지
const TeamLogoImage = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.06}px;
  height: ${({ width }) => width * 0.06}px;
  margin-horizontal: ${({ width }) => width * 0.01}px;
`;
const ScheduleTime = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
  margin-left: 2px;
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

// 세로 구분선 컴포넌트 추가
const VerticalDivider = styled.View<StyledProps>`
  width: 1px;
  background-color: #EEEEEE;
  height: 100%;
  margin: 0 ${({ width }) => width * 0.02}px;
`;

// 일정 컨테이너 스타일 추가
const SchedulesContainer = styled.View`
  flex-direction: row;
  width: 100%;
  justify-content: center;
`;

// 일정 열 컨테이너 스타일 추가
const SchedulesColumn = styled.View`
  flex: 1;
`;

// 이미 존재하는 HistoryLeftGroup을 활용하여 날짜, 로고, 결과 그룹화
const HistoryLeftGroup = styled.View`
  flex-direction: row;
  align-items: center;
  flex: 1;
`;

const MainPage = () => {
  const tabNavigation = useNavigation<TabNavigationProp>();
  const stackNavigation = useNavigation<MainPageNavigationProp>();
  const { teamColor, teamName, setTeamData } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const {
    accountInfo,
    isLoading: accountLoading,
    error: accountError,
    fetchAccountInfo,
  } = useAccountStore();
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
  const [teamRank, setTeamRank] = useState<number | null>(null);
  const [rankChange, setRankChange] = useState<number | null>(null);
  const [isRankLoading, setIsRankLoading] = useState<boolean>(true);
  // 경기 일정 관련 상태 추가
  const [gameSchedules, setGameSchedules] = useState<GameSchedule[]>([]);
  const [isScheduleLoading, setIsScheduleLoading] = useState<boolean>(true);
  const [scheduleError, setScheduleError] = useState<Error | null>(null);
  // 일일 리포트 관련 상태 추가
  const [dailyReport, setDailyReport] = useState<{
    TEAM_ID: number;
    DATE: string;
    LLM_CONTEXT: string;
    TEAM_AVG_AMOUNT: number | null;
    DAILY_REPORT_ID: number;
  } | null>(null);
  const [isDailyReportLoading, setIsDailyReportLoading] =
    useState<boolean>(true);
  const [dailyReportError, setDailyReportError] = useState<Error | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<TransactionItem[]>([]);
  const [isRecentTransactionsLoading, setIsRecentTransactionsLoading] = useState<boolean>(true);
  // 우대금리 정보 상태 추가
  const [interestDetails, setInterestDetails] = useState<InterestDetails | null>(null);
  const [isInterestLoading, setIsInterestLoading] = useState<boolean>(true);

  // 계좌 정보 조회 - useAccountStore 사용
  useEffect(() => {
    fetchAccountInfo();
    fetchInterestDetails();
  }, []);
  // 팀 ID 가져오기 함수
  const getTeamIdByName = (name: string | undefined): number => {
    if (!name) return 1; // 기본값으로 1 반환
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

  // 일일 리포트 조회
  useEffect(() => {
    const fetchDailyReport = async () => {
      try {
        setIsDailyReportLoading(true);
        const teamId = getTeamIdByName(teamName);
        console.log("일일 리포트 요청 - 팀 ID:", teamId);

        const response = await api.get(`/api/report/daily/team/${teamId}`);
        console.log("일일 리포트 API 응답:", response.data);
        
        if (response.status === 200 && response.data) {
          setDailyReport(response.data);
        } else {
          console.error("API 응답 형식 오류:", response);
          throw new Error("API 응답 형식이 올바르지 않습니다");
        }
      } catch (err) {
        console.error("일일 리포트 조회 실패:", err);
        setDailyReportError(
          err instanceof Error ? err : new Error("알 수 없는 오류")
        );
      } finally {
        setIsDailyReportLoading(false);
      }
    };

    if (teamName) {
      fetchDailyReport();
    }
  }, [teamName]);

  // 경기 일정 조회
  useEffect(() => {
    const fetchGameSchedules = async () => {
      try {
        setIsScheduleLoading(true);

        // 팀명으로 팀 ID 가져오기
        const teamId = getTeamIdByName(teamName);

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
            .slice(0, 6); // 다음 6개 경기만 선택

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
    if (teamName) {
      fetchGameSchedules();
    }
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

          const change = currentTeam.BEFORE_RANK - currentTeam.RANK;
          setRankChange(change);
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
  // 적금 규칙 인터페이스 정의 (API 응답 구조에 맞춤)
  interface SavingRule {
    USER_SAVING_RULED_ID: number;
    ACCOUNT_ID: number;
    SAVING_RULE_TYPE_ID: number;
    SAVING_RULE_TYPE_NAME: string;
    SAVING_RULE_DETAIL_ID: number;
    PLAYER_TYPE_ID: number | null;
    PLAYER_TYPE_NAME: string | null;
    USER_SAVING_RULED_AMOUNT: number;
    PLAYER_ID: number | null;
    PLAYER_NAME: string | null;
    RECORD_NAME: string;
  }

  // 기존 함수를 대체할 실제 API 호출 함수
  const fetchRules = async () => {
    try {
      const response = await api.get("/api/account/saving-rules");
      console.log("적금 규칙 API 응답:", response.data);
      return response.data;
    } catch (err) {
      console.error("규칙 조회 실패:", err);
      return [];
    }
  };

  // 규칙을 SAVING_RULE_TYPE_ID 기준으로 분류하는 함수
  const organizeRulesByType = (
    rules: SavingRule[],
    userPreferredPlayerType?: number | null
  ) => {
    // SAVING_RULE_TYPE_ID 기반 그룹화
    const rulesByTypeId: { [key: number]: SavingRule[] } = {};
    rules.forEach((rule) => {
      const typeId = rule.SAVING_RULE_TYPE_ID;
      if (!rulesByTypeId[typeId]) {
        rulesByTypeId[typeId] = [];
      }
      rulesByTypeId[typeId].push(rule);
    });
    const organizedRules: RuleItem[] = [];

    // 기본 규칙 (ID: 1) 항상 포함
    if (rulesByTypeId[1]?.length > 0) {
      organizedRules.push({
        id: 1,
        title: "기본 규칙",
        rules: rulesByTypeId[1].map(
          (r) =>
            `${r.RECORD_NAME}: ${r.USER_SAVING_RULED_AMOUNT.toLocaleString()}원`
        ),
      });
    }

    // 투수 규칙 (ID: 2) - 최애 선수가 투수인 경우 또는 필터링 없을 때만 포함
    if (
      rulesByTypeId[2]?.length > 0 &&
      (userPreferredPlayerType === 1 || !userPreferredPlayerType)
    ) {
      organizedRules.push({
        id: 2,
        title: "투수 규칙",
        rules: rulesByTypeId[2].map(
          (r) =>
            `${r.PLAYER_NAME ? r.PLAYER_NAME + ": " : ""}${
              r.RECORD_NAME
            }: ${r.USER_SAVING_RULED_AMOUNT.toLocaleString()}원`
        ),
      });
    }

    // 타자 규칙 (ID: 3) - 최애 선수가 타자인 경우 또는 필터링 없을 때만 포함
    if (
      rulesByTypeId[3]?.length > 0 &&
      (userPreferredPlayerType === 2 || !userPreferredPlayerType)
    ) {
      organizedRules.push({
        id: 3,
        title: "타자 규칙",
        rules: rulesByTypeId[3].map(
          (r) =>
            `${r.PLAYER_NAME ? r.PLAYER_NAME + ": " : ""}${
              r.RECORD_NAME
            }: ${r.USER_SAVING_RULED_AMOUNT.toLocaleString()}원`
        ),
      });
    }

    // 상대팀 규칙 (ID: 4) 항상 포함
    if (rulesByTypeId[4]?.length > 0) {
      organizedRules.push({
        id: 4,
        title: "상대팀 규칙",
        rules: rulesByTypeId[4].map(
          (r) =>
            `${r.RECORD_NAME}: ${r.USER_SAVING_RULED_AMOUNT.toLocaleString()}원`
        ),
      });
    }

    return organizedRules;
  };

  // 팀 로고 임포트
  const teamLogos = {
    KIA: require("../../assets/kbo/tigers.png"),
    SAMSUNG: require("../../assets/kbo/lions.png"),
    LG: require("../../assets/kbo/twins.png"),
    DOOSAN: require("../../assets/kbo/bears.png"),
    KT: require("../../assets/kbo/wiz.png"),
    SSG: require("../../assets/kbo/landers.png"),
    LOTTE: require("../../assets/kbo/giants.png"),
    HANWHA: require("../../assets/kbo/eagles.png"),
    NC: require("../../assets/kbo/dinos.png"),
    KIWOOM: require("../../assets/kbo/heroes.png"),
  };

  // 팀명으로 팀 로고 가져오기
  const getTeamLogo = (teamName: string) => {
    // 전체 팀명과 약칭 모두 매핑
    const logoMap: { [key: string]: any } = {
      // 전체 팀명 매핑
      "KIA 타이거즈": teamLogos.KIA,
      "삼성 라이온즈": teamLogos.SAMSUNG,
      "LG 트윈스": teamLogos.LG,
      "두산 베어스": teamLogos.DOOSAN,
      "KT 위즈": teamLogos.KT,
      "SSG 랜더스": teamLogos.SSG,
      "롯데 자이언츠": teamLogos.LOTTE,
      "한화 이글스": teamLogos.HANWHA,
      "NC 다이노스": teamLogos.NC,
      "키움 히어로즈": teamLogos.KIWOOM,

      // 약칭 매핑
      KIA: teamLogos.KIA,
      삼성: teamLogos.SAMSUNG,
      LG: teamLogos.LG,
      두산: teamLogos.DOOSAN,
      KT: teamLogos.KT,
      SSG: teamLogos.SSG,
      롯데: teamLogos.LOTTE,
      한화: teamLogos.HANWHA,
      NC: teamLogos.NC,
      키움: teamLogos.KIWOOM,
    };

    return logoMap[teamName] || teamLogos.NC; // 매칭 실패 시 NC 로고를 기본값으로 사용
  };

  // 최근 거래 내역 가져오기 함수 수정
  const fetchRecentTransactions = async () => {
    try {
      setIsRecentTransactionsLoading(true);
      const response = await api.get('/api/account/transfers_log', {
        params: { month: new Date().getMonth() + 1 }
      });
      
      // 경기 결과 API를 호출하여 상대팀 정보 가져오기
      const resultsResponse = await api.get('/api/game/user-team-results');
      console.log("경기 결과 API 응답:", resultsResponse.data);
      
      const gameResults = resultsResponse.data.reduce((acc: { [key: string]: any }, result: any) => {
        acc[result.game_date] = result;
        return acc;
      }, {});
      
      console.log("거래 내역 API 응답:", response.data);
      
      // API 응답을 TransactionItem 형식으로 변환하고 최근 3개만 선택
      const transactions: TransactionItem[] = response.data
        .map((item: any) => {
          const dateObj = new Date(item.DATE);
          const formattedDate = `${dateObj.getMonth() + 1}/${dateObj.getDate()}`;
          
          // 해당 날짜의 경기 결과에서 상대팀 정보와 승패 결과 가져오기
          const gameResult = gameResults[item.DATE];
          console.log(`${item.DATE} 날짜의 경기 결과:`, gameResult);
          
          const opponentTeamName = gameResult?.opponent_team_name || "";
          
          // 경기 결과 상태 결정
          let status: GameStatus = "upcoming";
          
          if (gameResult) {
            // API 응답의 result 값에 따라 상태 결정
            const result = gameResult.result?.toString().toLowerCase() || "";
            
            if (result.includes("win") || result.includes("승리")) {
              status = "win";
            } else if (result.includes("los") || result.includes("패배")) {
              status = "lose";
            } else if (result.includes("draw") || result.includes("tie") || result.includes("무승부")) {
              status = "draw";
            } else if (result.includes("cancel") || result.includes("취소")) {
              status = "cancelled";
            }
          }
          
          // 한국어 결과 텍스트
          let resultText: string;
          switch (status) {
            case "win": resultText = "승"; break;
            case "lose": resultText = "패"; break;
            case "draw": resultText = "무"; break;
            case "cancelled": resultText = "취소"; break;
            default: resultText = "경기전"; break;
          }
          
          return {
            id: item.DATE,
            opponent: opponentTeamName,
            date: formattedDate,
            description: item.TEXT,
            amount: item.AMOUNT,
            wins: 1,
            result: resultText,
            status: status
          };
        })
        .slice(0, 3); // 최근 3개만 선택
      
      console.log("변환된 거래 내역:", transactions);
      setRecentTransactions(transactions);
    } catch (error) {
      console.error("최근 거래 내역 조회 실패:", error);
      setRecentTransactions([]);
    } finally {
      setIsRecentTransactionsLoading(false);
    }
  };

  // 우대금리 정보 가져오기 함수 추가
  const fetchInterestDetails = async () => {
    try {
      setIsInterestLoading(true);
      const response = await api.get('/api/account/interest-details');
      console.log('우대금리 정보:', response.data);
      setInterestDetails(response.data);
    } catch (error) {
      console.error('우대금리 정보 가져오기 오류:', error);
    } finally {
      setIsInterestLoading(false);
    }
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
        
        // 우대금리 정보가 있을 경우 사용, 없으면 계좌 금리 사용
        if (interestDetails) {
          setInterestRate(interestDetails.base_interest_rate || 2.5);
          setAdditionalRate(interestDetails.mission_interest_rate || 0);
        } else {
          setInterestRate(account.interest_rate || 2.5);
          
          // 추가 금리 계산 (기본 금리 기준)
          const baseRate = 2.5; // 기본 금리 
          const additional = account.interest_rate - baseRate;
          setAdditionalRate(additional > 0 ? additional : 0);
        }

        // 목표 제목 설정 (간단한 예시)
        setSavingTitle(`${account.team_name || teamName} 적금`);

        // 규칙 데이터 가져오기 - API 호출
        const rulesData = await fetchRules();

        // 사용자의 선호 선수 타자 (1: 투수, 2: 타자)
        // 계정 정보에서 가져오거나 기본값 사용
        const preferredPlayerType = account.preferred_player_type || null;

        // API 응답 구조에 맞게 규칙 데이터 정리 및 필터링
        const organizedRules = organizeRulesByType(
          rulesData,
          preferredPlayerType
        );
        setSavingRules(organizedRules);

        // 최근 거래 내역 가져오기
        await fetchRecentTransactions();

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
  }, [accountInfo, interestDetails]);

  const percentage = Math.min(
    100,
    Math.round((currentAmount / (targetAmount || 1)) * 100) // 0으로 나누기 방지
  );
  const formatAmount = (amount: number) => {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };
  // 캐러셀 아이템 렌더링 함수
  const renderRuleItem = React.useCallback(
    ({ item }: { item: RuleItem }) => {
    return (
      <RuleCarouselCard width={width}>
        <RuleCardHeader width={width} teamColor={teamColor.primary}>
          <RuleCardTitle width={width}>{item.title}</RuleCardTitle>
            <Ionicons
              name="information-circle-outline"
              size={20}
              color="white"
            />
        </RuleCardHeader>
        <RuleCardContent width={width}>
            {item.rules.length > 0 ? (
              item.rules.map((rule: string, index: number) => (
            <RuleText key={index} width={width}>
              • {rule}
            </RuleText>
              ))
            ) : (
              <RuleText width={width}>• 설정된 규칙이 없습니다</RuleText>
            )}
        </RuleCardContent>
      </RuleCarouselCard>
    );
    },
    [width, teamColor.primary] // 의존성 배열에 width와 teamColor.primary 추가
  );

  // 캐러셀 컴포넌트
  const RulesCarousel = () => {
    const carouselRef = useRef(null);
    return (
      <View>
        <Carousel
          ref={carouselRef}
          loop={false}
          width={width - width * 0.12}
          height={width * 0.4}
          data={savingRules}
          scrollAnimationDuration={500}
          onSnapToItem={(index) => {
            console.log("캐러셀 스냅:", index);
          }}
          renderItem={renderRuleItem}
          defaultIndex={activeSlide}
          enabled={true}
          mode="parallax"
        />
      </View>
    );
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <BackButton onPress={() => stackNavigation.navigate("Home")}>
            <MaterialIcons name="chevron-left" size={28} color="white" />
          </BackButton>
          <HeaderTitle width={width}>
            야금야금
          </HeaderTitle>
          <View style={{ width: 40 }} />
        </Header>

        <SafeAreaView style={{ flex: 1, paddingBottom: 60 }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: 20 }}
          >
            {isLoading || accountLoading ? (
              <View
                style={{
                  padding: 10,
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <ActivityIndicator size="small" color={teamColor.primary} />
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
              <ProgressTitleContainer width={width}>
                <ProgressTitleLogo
                  width={width}
                  source={getTeamLogo(accountInfo?.savings_accounts?.[0]?.team_name || teamName || "NC")}
                  resizeMode="contain"
                />
                <ProgressTitle width={width}>{savingTitle}</ProgressTitle>
              </ProgressTitleContainer>
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
              <StatText width={width} style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                현재 금리: {interestRate.toFixed(1)}%
                {additionalRate > 0 && (
                  <StatHighlight status="up" style={{ marginLeft: 4 }}>
                    ↗ +{additionalRate.toFixed(1)}%
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
                    {!isRankLoading && rankChange !== null && (
                      <StatHighlight
                        status={
                          rankChange > 0
                            ? "up"
                            : rankChange < 0
                            ? "down"
                            : "same"
                        }
                      >
                        {rankChange > 0
                          ? `+${rankChange}`
                          : rankChange < 0
                          ? rankChange
                          : "±0"}
                      </StatHighlight>
                    )}
              </StatText>
            </StatsRow>

            <View style={{ padding: width * 0.04 }}>
              <Card width={width}>
                <CardHeader width={width}>
                      <CardTitle width={width}>오늘의 적금 비교</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                      {isDailyReportLoading ? (
                        <View style={{ padding: 10, alignItems: "center" }}>
                          <Text>일일 리포트 로딩 중...</Text>
                        </View>
                      ) : dailyReportError ? (
                        <View style={{ padding: 10, alignItems: "center" }}>
                          <Text>일일 리포트를 불러오는데 실패했습니다.</Text>
                        </View>
                      ) : dailyReport && dailyReport.LLM_CONTEXT ? (
                  <CardText width={width}>
                          <RedText teamColor={teamColor.primary}>↗</RedText>{" "}
                          {dailyReport.LLM_CONTEXT}
                  </CardText>
                      ) : (
                        <CardText width={width}>
                          <RedText teamColor={teamColor.primary}>↗</RedText>{" "}
                          오늘의 적금 리포트를 불러올 수 없습니다.
                        </CardText>
                      )}
                </CardContent>
              </Card>

              {/* 적금 규칙 캐러셀 카드 */}
              <Card width={width}>
                <CardHeader width={width}>
                      <CardTitle width={width}>적금 규칙</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                      {/* savingRules 데이터가 있을 때만 RulesCarousel 렌더링 */}
                      {savingRules && savingRules.length > 0 ? (
                  <RulesCarousel />
                      ) : (
                        // 데이터 로딩 중이거나 없을 때 표시할 내용 (선택 사항)
                        <View style={{ padding: 10, alignItems: "center" }}>
                          <Text>규칙 로딩 중...</Text>
                        </View>
                      )}
                </CardContent>
              </Card>

                  {/* 최근 적금 내역 카드 */}
              <Card width={width}>
                <CardHeader width={width}>
                      <CardTitle width={width}>최근 적금 내역</CardTitle>
                  <TouchableOpacity
                    onPress={() => {
                          tabNavigation.navigate("적금내역", {
                            viewMode: "list",
                      });
                    }}
                  >
                    <ViewAllLink width={width} teamColor={teamColor.primary}>
                      전체 내역 &gt;
                    </ViewAllLink>
                  </TouchableOpacity>
                </CardHeader>
                <CardContent width={width}>
                      {isRecentTransactionsLoading ? (
                        <View style={{ padding: 10, alignItems: "center" }}>
                          <Text>거래 내역 로딩 중...</Text>
                        </View>
                      ) : recentTransactions.length > 0 ? (
                        recentTransactions.map((transaction) => (
                          <HistoryItem key={transaction.id} width={width}>
                            <HistoryLeftGroup>
                              <HistoryDate width={width}>{transaction.date}</HistoryDate>
                              <TeamLogo
                                width={width}
                                source={getTeamLogo(transaction.opponent)}
                              />
                              <ResultText 
                                width={width} 
                                status={transaction.status}
                              >
                                {transaction.result}
                              </ResultText>
                            </HistoryLeftGroup>
                            <HistoryAmount width={width} teamColor={teamColor.primary}>
                              +{transaction.amount.toLocaleString()}원
                            </HistoryAmount>
                          </HistoryItem>
                        ))
                      ) : (
                        <View style={{ padding: 10, alignItems: "center" }}>
                          <Text>최근 거래 내역이 없습니다.</Text>
                        </View>
                      )}
                </CardContent>
              </Card>

              {/* 다음 경기 일정 카드 */}
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
                    <SchedulesContainer>
                      {/* 왼쪽 3개 경기 */}
                      <SchedulesColumn>
                        {gameSchedules.slice(0, 3).map((game) => {
                          const isHomeGame =
                            game.HOME_TEAM_ID === getTeamIdByName(teamName);
                          const opponentTeam = isHomeGame
                            ? game.away_team_name
                            : game.home_team_name;
                          const gameDate = new Date(game.DATE);
                          const month = gameDate.getMonth() + 1;
                          const day = gameDate.getDate();
                          const location = isHomeGame ? "홈" : "원정";

                          return (
                            <ScheduleItem
                              key={game.GAME_SCHEDULE_KEY}
                              width={width}
                              onPress={() => {
                                tabNavigation.navigate("적금내역", {
                                  viewMode: "calendar",
                                });
                              }}
                            >
                              <ScheduleDate
                                width={width}
                              >{`${month}/${day}`}</ScheduleDate>
                              <TeamContainer>
                                <VsText width={width}>vs</VsText>
                                <TeamLogoImage 
                                  width={width}
                                  source={getTeamLogo(opponentTeam)}
                                  resizeMode="contain"
                                />
                                <ScheduleTime width={width}>
                                  {location}
                                </ScheduleTime>
                              </TeamContainer>
                            </ScheduleItem>
                          );
                        })}
                      </SchedulesColumn>
                      
                      {/* 세로 구분선 */}
                      <VerticalDivider width={width} />
                      
                      {/* 오른쪽 3개 경기 */}
                      <SchedulesColumn>
                        {gameSchedules.slice(3, 6).map((game) => {
                          const isHomeGame =
                            game.HOME_TEAM_ID === getTeamIdByName(teamName);
                          const opponentTeam = isHomeGame
                            ? game.away_team_name
                            : game.home_team_name;
                          const gameDate = new Date(game.DATE);
                          const month = gameDate.getMonth() + 1;
                          const day = gameDate.getDate();
                          const location = isHomeGame ? "홈" : "원정";

                          return (
                            <ScheduleItem
                              key={game.GAME_SCHEDULE_KEY}
                              width={width}
                              onPress={() => {
                                tabNavigation.navigate("적금내역", {
                                  viewMode: "calendar",
                                });
                              }}
                            >
                              <ScheduleDate
                                width={width}
                              >{`${month}/${day}`}</ScheduleDate>
                              <TeamContainer>
                                <VsText width={width}>vs</VsText>
                                <TeamLogoImage 
                                  width={width}
                                  source={getTeamLogo(opponentTeam)}
                                  resizeMode="contain"
                                />
                                <ScheduleTime width={width}>
                                  {location}
                                </ScheduleTime>
                              </TeamContainer>
                            </ScheduleItem>
                          );
                        })}
                      </SchedulesColumn>
                    </SchedulesContainer>
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
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default MainPage;


