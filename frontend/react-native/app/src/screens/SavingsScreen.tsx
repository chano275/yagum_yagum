// SavingsScreen.tsx
import React, { useState, useMemo, useEffect, useRef } from "react";
import {
  useWindowDimensions,
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  Text,
  Image,
  FlatList,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import * as Calendar from "expo-calendar";
import { Ionicons } from "@expo/vector-icons";
import { useTeam } from "@/context/TeamContext";
import { useRoute, useNavigation } from "@react-navigation/native";
import { useFocusEffect } from "@react-navigation/native";
import { api } from "@/api/axios";

// 동적 스타일링을 위한 인터페이스
interface StyledProps {
  width: number;
}

// 뷰 모드 타입
type ViewMode = "calendar" | "list";

// 간소화된 경기 상태 타입
type GameStatus = "win" | "lose" | "draw" | "cancelled" | "upcoming";

// 경기 데이터 타입 정의
interface GameSchedule {
  DATE: string;
  HOME_TEAM_ID: number;
  AWAY_TEAM_ID: number;
  GAME_SCHEDULE_KEY: number;
  home_team_name: string;
  away_team_name: string;
  status?: GameStatus; // API에는 없지만 UI를 위해 추가
  amount?: number | null; // API에는 없지만 UI를 위해 추가
}

// 캘린더에 표시할 마킹 데이터 타입
interface MarkingData {
  gameResult?: GameStatus;
  amount?: number | null;
  teamLogo?: any;
  fixture?: GameSchedule;
}

// 3연전 시리즈 데이터 타입
interface SeriesMatch {
  id: string;
  homeTeam: {
    name: string;
    logo: any;
  };
  awayTeam: {
    name: string;
    logo: any;
  };
  dateRange: string;
  result: string;
  days: {
    date: string;
    amount: number | null;
    status: GameStatus; // 상태 필드 추가
  }[];
  totalAmount: number;
  status?: "current" | "past" | "upcoming";
  startTime?: number;
  isStartingToday?: boolean;
}

// 커스텀 캘린더 날짜 타입
interface CalendarDay {
  date: Date;
  dateString: string;
  day: number;
  month: number;
  year: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  marking?: MarkingData;
}

// 거래 내역 아이템 타입
interface TransactionItem {
  id: string;
  opponent: string;
  date: string;
  description: string;
  amount: number;
  wins: number;
}

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// 날짜 포맷 변환 함수들
const formatShortDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

const formatYYYYMMDD = (date: Date): string => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
    2,
    "0"
  )}-${String(date.getDate()).padStart(2, "0")}`;
};

const isConsecutiveDates = (dates: string[]): boolean => {
  if (dates.length < 2) return true;

  const timestamps = dates.map((date) => new Date(date).getTime());
  timestamps.sort((a, b) => a - b);

  for (let i = 1; i < timestamps.length; i++) {
    const diff = timestamps[i] - timestamps[i - 1];
    // 일반적으로 연속된 날짜는 하루 차이 (86400000 밀리초)
    // 여기서는 1.5일까지 허용 (시간 차이 감안)
    if (diff > 130000000) {
      return false;
    }
  }
  return true;
};

// 스타일 컴포넌트 정의
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

const HeaderRight = styled.View`
  flex-direction: row;
  align-items: center;
`;

const IconButton = styled.TouchableOpacity<{ isActive?: boolean }>`
  margin-left: 15px;
  opacity: ${(props) => (props.isActive ? 1 : 0.6)};
`;

const Card = styled.View<StyledProps>`
  background-color: white;
  border-radius: 16px;
  margin-bottom: ${({ width }) => width * 0.04}px;
  overflow: hidden;
  border-width: 1px;
  border-color: #eeeeee;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.06);
  `}
`;

const CardHeader = styled.View<StyledProps>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: ${({ width }) => width * 0.035}px ${({ width }) => width * 0.04}px;
  border-bottom-width: 1px;
  border-bottom-color: #f5f5f5;
`;

const CardTitle = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.042}px;
  font-weight: bold;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const CardContent = styled.View<StyledProps>`
  padding: ${({ width }) => width * 0.03}px;
`;

const CalendarCard = styled(Card)`
  padding: 0;
`;

// 커스텀 캘린더 스타일 컴포넌트
const CalendarContainer = styled.View`
  background-color: white;
  padding-bottom: 10px;
  padding-horizontal: 6px;
`;

const CalendarHeaderContainer = styled.View`
  flex-direction: column;
  align-items: center;
  padding: 12px 16px 8px 16px;
`;

const MonthRow = styled.View`
  flex-direction: row;
  align-items: center;
  width: 100%;
  justify-content: space-between;
  margin-bottom: 10px;
`;

const MonthTitleContainer = styled.View`
  flex: 1;
  align-items: center;
  justify-content: center;
`;

const MonthTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  color: #333;
`;

const WeekdayRow = styled.View`
  flex-direction: row;
  margin-bottom: 8px;
  padding-horizontal: 8px;
`;

const WeekdayText = styled.Text`
  flex: 1;
  text-align: center;
  font-size: 12px;
  color: #666;
`;

const DaysContainer = styled.View`
  flex-wrap: wrap;
  flex-direction: row;
  padding-left: 2px;
`;

const DayCell = styled.TouchableOpacity<{
  isToday: boolean;
  isSelected: boolean;
  isCurrentMonth: boolean;
  backgroundColor: string;
  teamColor: string;
}>`
  width: ${100 / 7}%;
  height: 68px; // 고정 높이로 변경
  align-items: center;
  justify-content: space-between; // 내용을 균등하게 분배
  padding: 4px 2px 3px 2px; // 상하좌우 패딩 추가
  opacity: ${(props) => (props.isCurrentMonth ? 1 : 0.4)};
  background-color: ${(props) => props.backgroundColor};
  border-width: ${(props) => (props.isToday || props.isSelected ? 1 : 0)}px;
  border-color: ${(props) => props.teamColor};
`;

// 3연전 관련 컴포넌트
const SeriesCard = styled.View`
  background-color: white;
  border-radius: 12px;
  margin-bottom: 16px;
  border-width: 1px;
  border-color: #eeeeee;
  overflow: hidden;
`;

const SeriesHeader = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
`;

const TeamVsContainer = styled.View`
  flex-direction: row;
  align-items: center;
`;

const TeamLogo = styled.Image`
  width: 30px;
  height: 30px;
  border-radius: 15px;
`;

const VsText = styled.Text`
  margin: 0 8px;
  font-size: 14px;
  color: #666;
`;

const DateRangeText = styled.Text`
  font-size: 14px;
  color: #666;
  margin-left: 8px;
`;

const ResultBadge = styled.View`
  background-color: #e8f4ff;
  padding: 6px 12px;
  border-radius: 20px;
`;

const ResultText = styled.Text`
  color: #0066cc;
  font-size: 12px;
  font-weight: bold;
`;

const DayRowContainer = styled.View`
  flex-direction: row;
  padding: 0 10px;
`;

const DayBox = styled.View<{ backgroundColor: string }>`
  flex: 1;
  background-color: ${(props) => props.backgroundColor};
  padding: 15px 10px;
  margin: 5px;
  border-radius: 8px;
  align-items: center;
`;

const DayText = styled.Text`
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
`;

const AmountText = styled.Text<{ color: string }>`
  color: ${(props) => props.color};
  font-size: 16px;
  font-weight: bold;
`;

const TotalContainer = styled.View`
  flex-direction: row;
  justify-content: space-between;
  padding: 14px 16px;
  border-top-width: 1px;
  border-top-color: #f0f0f0;
  margin-top: 6px;
`;

const TotalLabel = styled.Text`
  font-size: 14px;
  color: #666;
`;

const TotalAmount = styled.Text`
  font-size: 16px;
  font-weight: bold;
  color: #000;
`;

// 상세 내역 리스트 뷰 스타일 컴포넌트
const ListMonthNavigator = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const ListMonthTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
  color: #333;
`;

const TransactionItem = styled.View`
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const TransactionHeader = styled.View`
  flex-direction: row;
  padding: 16px;
  justify-content: space-between;
  align-items: center;
`;

const TeamInfoContainer = styled.View`
  flex-direction: row;
  align-items: center;
  flex: 1;
`;

const TransactionAmountText = styled.Text`
  font-size: 16px;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

const TransactionDescription = styled.View`
  padding: 12px;
  padding-top: 0;
  background-color: #f9f9f9;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const DescriptionText = styled.Text`
  font-size: 14px;
  color: #333;
`;

const WinsText = styled.Text`
  font-size: 12px;
  color: #888;
  margin-top: 4px;
`;

const SavingsScreen = () => {
  const { teamColor, teamName } = useTeam();
  const route = useRoute();
  const navigation = useNavigation();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 상태 변수
  const [viewMode, setViewMode] = useState<ViewMode>("calendar");
  const [selectedDate, setSelectedDate] = useState<string>(
    formatYYYYMMDD(new Date())
  );
  const [currentMonth, setCurrentMonth] = useState<Date>(new Date());
  const [calendarDays, setCalendarDays] = useState<CalendarDay[]>([]);
  const [gameSchedules, setGameSchedules] = useState<GameSchedule[]>([]);
  const [seriesMatches, setSeriesMatches] = useState<SeriesMatch[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeriesLoading, setIsSeriesLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [calendarPermission, setCalendarPermission] = useState<boolean>(false);
  const [transactionItems, setTransactionItems] = useState<TransactionItem[]>(
    []
  );

  // 네비게이션 파라미터 처리
  useFocusEffect(
    React.useCallback(() => {
      const params = route.params;
      let mode: ViewMode = "calendar";

      if (params && typeof params === "object") {
        if ("viewMode" in params) {
          mode = params.viewMode as ViewMode;
        } else if (params.params && "viewMode" in params.params) {
          mode = params.params.viewMode as ViewMode;
        }
      }

      if (mode === "calendar" || mode === "list") {
        setViewMode(mode);
      }
    }, [route.params])
  );

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

  // 캘린더 권한 요청
  useEffect(() => {
    (async () => {
      const { status } = await Calendar.requestCalendarPermissionsAsync();
      setCalendarPermission(status === "granted");

      if (status === "granted") {
        // 여기서 시스템 캘린더 이벤트를 가져오는 로직을 구현할 수 있습니다
        // 예: const calendars = await Calendar.getCalendarsAsync();
      }
    })();
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
    return teamMapping[name] || 1; // 기본값 1
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

      // 영문 약칭 매핑
      TIGERS: teamLogos.KIA,
      LIONS: teamLogos.SAMSUNG,
      TWINS: teamLogos.LG,
      BEARS: teamLogos.DOOSAN,
      WIZ: teamLogos.KT,
      LANDERS: teamLogos.SSG,
      GIANTS: teamLogos.LOTTE,
      EAGLES: teamLogos.HANWHA,
      DINOS: teamLogos.NC,
      HEROES: teamLogos.KIWOOM,
    };

    return logoMap[teamName] || teamLogos.NC; // 매칭 실패 시 NC 로고를 기본값으로 사용
  };

  // 거래 상세 내역 페이지로 이동하는 함수
  const handleTransactionPress = (id: string) => {
    navigation.navigate("TransactionDetail", { id });
  };

  // 3연전 시리즈 식별 함수
  const identifySeriesMatches = (games: GameSchedule[]): SeriesMatch[] => {
    const seriesMatchesData: SeriesMatch[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0); // 오늘 날짜의 시작 시간으로 설정

    if (!games.length) return seriesMatchesData;

    // 팀 ID 조합으로 그룹화
    const matchesByTeams: { [key: string]: GameSchedule[] } = {};

    games.forEach((game) => {
      const teams = [game.HOME_TEAM_ID, game.AWAY_TEAM_ID].sort().join("-");
      if (!matchesByTeams[teams]) {
        matchesByTeams[teams] = [];
      }
      matchesByTeams[teams].push(game);
    });

    // 모든 3연전 시리즈 찾기
    const allSeries: SeriesMatch[] = [];

    // 각 팀 조합별로 연속 3경기(3연전) 찾기
    Object.values(matchesByTeams).forEach((teamGames) => {
      // 날짜 기준 정렬
      teamGames.sort(
        (a, b) => new Date(a.DATE).getTime() - new Date(b.DATE).getTime()
      );

      // 연속된 3경기 이상 찾기
      for (let i = 0; i <= teamGames.length - 3; i++) {
        const potentialSeries = teamGames.slice(i, i + 3);
        const dates = potentialSeries.map((game) => game.DATE);

        if (isConsecutiveDates(dates)) {
          // 경기 날짜 포맷팅
          const startDate = formatShortDate(potentialSeries[0].DATE);
          const endDate = formatShortDate(
            potentialSeries[potentialSeries.length - 1].DATE
          );

          // 시리즈의 첫 경기 날짜와 마지막 경기 날짜
          const firstGameDate = new Date(potentialSeries[0].DATE);
          firstGameDate.setHours(0, 0, 0, 0);
          const lastGameDate = new Date(
            potentialSeries[potentialSeries.length - 1].DATE
          );
          lastGameDate.setHours(0, 0, 0, 0);

          // 시리즈 상태 결정 (진행 중/과거/미래)
          let seriesStatus = "upcoming";
          if (lastGameDate < today) {
            seriesStatus = "past"; // 3연전이 모두 지난 경우
          } else if (firstGameDate <= today && today <= lastGameDate) {
            seriesStatus = "current"; // 3연전이 진행 중인 경우
          }

          // 각 경기별 상세 정보 - 하드코딩 데이터 추가
          const sampleStatuses: GameStatus[] = ["win", "lose", "upcoming"];
          const sampleAmounts = [5000, 7500, 10000];

          const days = potentialSeries.map((game, index) => ({
            date: formatShortDate(game.DATE),
            amount: sampleAmounts[index % 3], // 인덱스가 3을 초과하지 않도록 modulo 연산
            status: sampleStatuses[index % 3], // 인덱스가 3을 초과하지 않도록 modulo 연산
          }));

          // 총 적립액 계산
          const totalAmount = days.reduce(
            (sum, day) => sum + (day.amount || 0),
            0
          );

          // 홈팀과 원정팀 결정
          const homeTeam = {
            name: potentialSeries[0].home_team_name.split(" ")[0],
            logo: getTeamLogo(potentialSeries[0].home_team_name),
          };

          const awayTeam = {
            name: potentialSeries[0].away_team_name.split(" ")[0],
            logo: getTeamLogo(potentialSeries[0].away_team_name),
          };

          // 오늘 시작하는지 확인
          const isStartingToday =
            firstGameDate.getFullYear() === today.getFullYear() &&
            firstGameDate.getMonth() === today.getMonth() &&
            firstGameDate.getDate() === today.getDate();

          // 시리즈 정보 추가
          allSeries.push({
            id: `series-${allSeries.length + 1}`,
            homeTeam,
            awayTeam,
            dateRange: `${startDate} ~ ${endDate}`,
            result: seriesStatus === "past" ? "지난 경기" : "예정된 경기",
            days,
            totalAmount: totalAmount, // 자동 계산된 총액
            status: seriesStatus,
            startTime: firstGameDate.getTime(),
            isStartingToday,
          });
        }
      }
    });

    // 우선순위에 따라 시리즈 정렬 및 선택
    // 1. 현재 진행 중인 시리즈
    const currentSeries = allSeries
      .filter((series) => series.status === "current")
      .sort((a, b) => {
        // 정렬 기준 1: 오늘 시작하는 시리즈가 최우선
        if (a.isStartingToday && !b.isStartingToday) return -1;
        if (!a.isStartingToday && b.isStartingToday) return 1;

        // 정렬 기준 2: 시작 시간이 최신인 것 (역순)
        return b.startTime - a.startTime;
      });

    // 2. 과거 시리즈 (최신순)
    const pastSeries = allSeries
      .filter((series) => series.status === "past")
      .sort((a, b) => b.startTime - a.startTime);

    // 3. 결과 구성: 항상 총 3개의 시리즈가 출력되도록 수정
    const maxDisplayCount = 3; // 총 표시할 시리즈 수
    const result = [];

    // 현재 진행 중인 시리즈 모두 추가
    result.push(...currentSeries);

    // 남은 자리를 과거 시리즈로 채우기
    const remainingSlots = Math.max(0, maxDisplayCount - result.length);
    if (remainingSlots > 0) {
      result.push(...pastSeries.slice(0, remainingSlots));
    }

    // 최종적으로 최대 3개까지만 표시
    return result.slice(0, maxDisplayCount);
  };

  // 월별 거래 내역 데이터 가져오기 (임시 더미 데이터)
  const fetchTransactionsForMonth = (month: Date) => {
    // 추후 API 호출로 변경될 예정
    // 현재는 더미 데이터 반환
    const dummyTransactions: TransactionItem[] = [
      {
        id: "1",
        opponent: "TWINS",
        date: "3/12",
        description: "최형우의 시원한 홈런포로 팀이 승리...",
        amount: 15000,
        wins: 3,
      },
      {
        id: "2",
        opponent: "TWINS",
        date: "3/11",
        description: "아쉽게도 경기를 내줬지만, 내일을 기약...",
        amount: 2000,
        wins: 1,
      },
      {
        id: "3",
        opponent: "BEARS",
        date: "3/8",
        description: "치열한 접전 끝에 아쉽게 패배했습니다...",
        amount: 3000,
        wins: 1,
      },
    ];

    setTransactionItems(dummyTransactions);
  };

  // API에서 경기 일정 가져오기
  useEffect(() => {
    const fetchGameSchedules = async () => {
      try {
        setIsLoading(true);
        setIsSeriesLoading(true);

        // 팀명으로 팀 ID 가져오기
        const teamId = getTeamIdByName(teamName);
        console.log("팀 ID로 경기일정 조회:", teamId);

        // API 호출
        const response = await api.get(`/api/game/schedule/team/${teamId}`);

        if (response.status === 200 && Array.isArray(response.data)) {
          // API 응답 로그 출력
          console.log(`경기 일정 ${response.data.length}개 조회 성공`);

          // 경기 일정 데이터 설정
          setGameSchedules(response.data);

          // 3연전 시리즈 식별
          const seriesData = identifySeriesMatches(response.data);
          setSeriesMatches(seriesData);
        } else {
          throw new Error("API 응답 형식이 올바르지 않습니다");
        }
      } catch (err) {
        console.error("경기 일정 조회 실패:", err);
        setError(err instanceof Error ? err : new Error("알 수 없는 오류"));
        // 에러 시 빈 배열 설정
        setGameSchedules([]);
        setSeriesMatches([]);
      } finally {
        setIsLoading(false);
        setIsSeriesLoading(false);
      }
    };

    if (teamName) {
      fetchGameSchedules();
    }
  }, [teamName]); // 팀 변경시 다시 불러오기

  // 거래 내역 초기 로드
  useEffect(() => {
    fetchTransactionsForMonth(currentMonth);
  }, []);

  // 날짜별 경기 일정 및 마킹 데이터 생성
  const markedDates = useMemo(() => {
    if (isLoading || !gameSchedules.length) return {};

    const markingsData: { [date: string]: MarkingData } = {};

    gameSchedules.forEach((game) => {
      // 현재 팀이 홈팀인지 원정팀인지 확인
      const isHomeTeam = game.HOME_TEAM_ID === getTeamIdByName(teamName);
      const opponentTeam = isHomeTeam
        ? game.away_team_name
        : game.home_team_name;

      // 모든 경기를 "upcoming"으로 설정 (무작위 값 대신 고정 값 사용)
      const status: GameStatus = "upcoming";
      const amount: number | null = null;

      const gameWithStatus = {
        ...game,
        status,
        amount,
      };

      markingsData[game.DATE] = {
        gameResult: status,
        amount: amount,
        teamLogo: getTeamLogo(opponentTeam),
        fixture: gameWithStatus,
      };
    });

    return markingsData;
  }, [gameSchedules, teamName]);

  // 선택한 날짜의 경기 정보
  const selectedFixture = useMemo(() => {
    if (!selectedDate || !markedDates[selectedDate]) return null;
    return markedDates[selectedDate].fixture;
  }, [selectedDate, markedDates]);

  // 캘린더 날짜 생성 함수
  const generateCalendarDays = (month: Date) => {
    const year = month.getFullYear();
    const monthIndex = month.getMonth();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // 해당 월의 첫 날과 마지막 날 구하기
    const firstDayOfMonth = new Date(year, monthIndex, 1);
    const lastDayOfMonth = new Date(year, monthIndex + 1, 0);

    // 첫 주의 시작일 (이전 달의 일부 날짜 포함)
    const startDate = new Date(firstDayOfMonth);
    startDate.setDate(startDate.getDate() - startDate.getDay());

    // 마지막 주의 종료일 (다음 달의 일부 날짜 포함)
    const endDate = new Date(lastDayOfMonth);
    const remainingDays = 6 - endDate.getDay();
    endDate.setDate(endDate.getDate() + remainingDays);

    const days: CalendarDay[] = [];
    let currentDate = new Date(startDate);

    // 캘린더에 표시할 모든 날짜 생성
    while (currentDate <= endDate) {
      const dateString = formatYYYYMMDD(currentDate);

      days.push({
        date: new Date(currentDate),
        dateString,
        day: currentDate.getDate(),
        month: currentDate.getMonth() + 1,
        year: currentDate.getFullYear(),
        isCurrentMonth: currentDate.getMonth() === monthIndex,
        isToday: formatYYYYMMDD(currentDate) === formatYYYYMMDD(today),
        isSelected: dateString === selectedDate,
        marking: markedDates[dateString],
      });

      currentDate.setDate(currentDate.getDate() + 1);
    }

    return days;
  };

  // 현재 월 변경 시 날짜 다시 생성
  useEffect(() => {
    const days = generateCalendarDays(currentMonth);
    setCalendarDays(days);
  }, [currentMonth, markedDates, selectedDate]);

  // 월 이동 함수
  const moveMonth = (addition: number) => {
    const newMonth = new Date(currentMonth);
    newMonth.setMonth(newMonth.getMonth() + addition);
    setCurrentMonth(newMonth);

    // 리스트 뷰에서는 거래 내역 다시 불러오기
    if (viewMode === "list") {
      fetchTransactionsForMonth(newMonth);
    }
  };

  // 요일 헤더 컴포넌트
  const renderWeekdayHeader = () => {
    const weekdays = ["일", "월", "화", "수", "목", "금", "토"];
    return (
      <WeekdayRow>
        {weekdays.map((day) => (
          <WeekdayText key={day}>{day}</WeekdayText>
        ))}
      </WeekdayRow>
    );
  };

  // 날짜 셀 렌더링 함수
  const renderDayCell = (day: CalendarDay) => {
    // 경기 결과에 따른 라벨 설정 (배경색은 제거)
    let bgColor = "transparent"; // 캘린더 셀 배경색을 투명하게 설정
    let statusLabel = "";
    let statusColor = "#333";
    let badgeBgColor = "transparent";

    if (day.marking) {
      const { gameResult } = day.marking;
      switch (gameResult) {
        case "win":
          statusLabel = "승";
          statusColor = "#f44336";
          badgeBgColor = "rgba(244, 67, 54, 0.2)";
          break;
        case "lose":
          statusLabel = "패";
          statusColor = "#2196f3";
          badgeBgColor = "rgba(33, 150, 243, 0.2)";
          break;
        case "draw":
          statusLabel = "무";
          statusColor = "#4caf50";
          badgeBgColor = "rgba(76, 175, 80, 0.2)";
          break;
        case "cancelled":
          statusLabel = "취소";
          statusColor = "#9e9e9e";
          badgeBgColor = "rgba(158, 158, 158, 0.2)";
          break;
        case "upcoming":
          statusLabel = "예정";
          statusColor = "#9c27b0";
          badgeBgColor = "rgba(156, 39, 176, 0.2)";
          break;
      }
    }

    // 선택된 날짜 또는 오늘 날짜의 배경색 변경
    if (day.isSelected) {
      bgColor = day.marking ? "transparent" : "#f0f0f0"; // 선택된 날짜도 투명하게 유지
    }

    return (
      <DayCell
        key={day.dateString}
        onPress={() => setSelectedDate(day.dateString)}
        isToday={day.isToday}
        isSelected={day.isSelected}
        isCurrentMonth={day.isCurrentMonth}
        backgroundColor={bgColor}
        teamColor={teamColor.primary}
      >
        {/* 날짜와 상태 표시 - 가로 배치로 변경 */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "flex-start",
            width: "100%",
            marginTop: 2,
          }}
        >
          <Text
            style={{
              fontSize: 14,
              color: day.isCurrentMonth ? "#333" : "#ccc",
              fontWeight: day.isToday || day.isSelected ? "bold" : "normal",
            }}
          >
            {day.day}
          </Text>

          {statusLabel ? (
            <View
              style={{
                paddingHorizontal: 4,
                paddingVertical: 1,
                borderRadius: 8,
                backgroundColor: badgeBgColor,
                marginLeft: 2,
              }}
            >
              <Text
                style={{
                  fontSize: 10,
                  fontWeight: "bold",
                  color: statusColor,
                }}
              >
                {statusLabel}
              </Text>
            </View>
          ) : null}
        </View>

        {/* 하단 영역: 금액과 로고 */}
        <View
          style={{
            alignItems: "center",
            justifyContent: "flex-end", // center에서 flex-end로 변경하여 하단 정렬
            marginTop: 0, // 2px에서 0px로 줄임
            marginBottom: 2, // 3px에서 2px로 줄임
            height: 32, // 고정 높이 설정으로 공간 효율화
          }}
        >
          {/* 적금 금액 */}
          {day.marking?.amount !== null &&
            day.marking?.amount !== undefined && (
              <Text
                style={{
                  fontSize: 10,
                  fontWeight: "bold",
                  color: teamColor.primary,
                  marginBottom: 1,
                }}
              >
                {day.marking.amount.toLocaleString()}원
              </Text>
            )}

          {/* 팀 로고 */}
          {day.marking?.teamLogo && (
            <Image
              source={day.marking.teamLogo}
              style={{
                width: 28, // 로고 크기 약간 증가
                height: 28,
              }}
              resizeMode="contain"
            />
          )}
        </View>
      </DayCell>
    );
  };

  // 커스텀 캘린더 렌더링
  const renderCustomCalendar = () => {
    return (
      <CalendarContainer>
        <CalendarHeaderContainer>
          <MonthRow>
            <TouchableOpacity
              onPress={() => moveMonth(-1)}
              style={{ padding: 10 }}
            >
              <Ionicons name="chevron-back" size={24} color="#666" />
            </TouchableOpacity>
            <MonthTitleContainer>
              <MonthTitle>{`${currentMonth.getFullYear()}년 ${
                currentMonth.getMonth() + 1
              }월`}</MonthTitle>
            </MonthTitleContainer>
            <TouchableOpacity
              onPress={() => moveMonth(1)}
              style={{ padding: 10 }}
            >
              <Ionicons name="chevron-forward" size={24} color="#666" />
            </TouchableOpacity>
          </MonthRow>
        </CalendarHeaderContainer>

        {renderWeekdayHeader()}

        <DaysContainer>
          {calendarDays.map((day) => renderDayCell(day))}
        </DaysContainer>
      </CalendarContainer>
    );
  };

  // 경기 상세 정보 카드 컴포넌트
  const FixtureDetailComponent = ({
    fixture,
  }: {
    fixture: GameSchedule | null;
  }) => {
    if (!fixture) return null;

    // 상대팀 정보만 구하기
    const isHomeTeam = fixture.HOME_TEAM_ID === getTeamIdByName(teamName);
    const opponent = isHomeTeam
      ? fixture.away_team_name
      : fixture.home_team_name;
    const opponentLogo = getTeamLogo(opponent);

    // 경기 장소 정보 추가
    const locationText = isHomeTeam ? "홈경기" : "원정경기";

    // 경기 상태 텍스트
    const getStatusText = (status?: GameStatus) => {
      if (!status) return "예정됨";

      switch (status) {
        case "win":
          return "승리";
        case "lose":
          return "패배";
        case "draw":
          return "무승부";
        case "cancelled":
          return "취소됨";
        case "upcoming":
          return "예정됨";
      }
    };

    return (
      <Card width={width} style={{ borderRadius: 16, overflow: "hidden" }}>
        <CardHeader
          width={width}
          style={{
            backgroundColor: "#f8f8f8",
            borderBottomWidth: 0,
          }}
        >
          <CardTitle width={width}>경기 상세 정보</CardTitle>
        </CardHeader>
        <CardContent width={width} style={{ padding: 16 }}>
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <Image
              source={opponentLogo}
              style={{ width: 36, height: 36, marginRight: 12 }}
              resizeMode="contain"
            />
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 18, fontWeight: "bold", color: "#333" }}>
                vs {opponent}
              </Text>
              <Text style={{ fontSize: 14, color: "#666", marginTop: 4 }}>
                {locationText}
              </Text>
            </View>
          </View>

          <View
            style={{
              flexDirection: "row",
              backgroundColor: "#f8f8f8",
              padding: 12,
              borderRadius: 12,
              marginBottom: 16,
            }}
          >
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 13, color: "#888" }}>일시</Text>
              <Text style={{ fontSize: 15, fontWeight: "500", marginTop: 4 }}>
                {fixture.DATE}
              </Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 13, color: "#888" }}>상태</Text>
              <Text
                style={{
                  fontSize: 15,
                  fontWeight: "600",
                  marginTop: 4,
                  color:
                    fixture.status === "win"
                      ? "#ff5555"
                      : fixture.status === "lose"
                      ? "#2196f3"
                      : "#333",
                }}
              >
                {getStatusText(fixture.status)}
              </Text>
            </View>
          </View>

          {fixture.amount !== null && fixture.amount !== undefined && (
            <View
              style={{
                backgroundColor: "#f0f8ff",
                padding: 12,
                borderRadius: 12,
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <Text style={{ fontSize: 15, color: "#333" }}>적립액</Text>
              <Text
                style={{
                  fontSize: 17,
                  fontWeight: "bold",
                  color: teamColor.primary,
                }}
              >
                {fixture.amount.toLocaleString()}원
              </Text>
            </View>
          )}
        </CardContent>
      </Card>
    );
  };

  // 3연전 시리즈 카드 컴포넌트 - React.memo로 최적화
  const SeriesMatchCard = React.memo(
    ({ match }: { match: SeriesMatch }) => {
      // 금액 포맷
      const formatAmount = (amount: number | null): string => {
        if (amount === null) return "-";
        return `${amount.toLocaleString()}원`;
      };

      // 상대팀 정보만 구하기
      const isMyTeamHome = match.homeTeam.name.includes(teamName.split(" ")[0]);
      const opponentTeam = isMyTeamHome ? match.awayTeam : match.homeTeam;
      const locationText = isMyTeamHome ? "홈" : "원정";

      // 진행 중인 시리즈에 특별한 스타일 적용
      const isCurrentSeries = match.status === "current";
      const badgeColor = isCurrentSeries ? "#1588CF" : "#e8f4ff";
      const badgeTextColor = isCurrentSeries ? "white" : "#0066cc";

      return (
        <SeriesCard
          style={{
            borderRadius: 16,
            marginBottom: 16,
            borderColor: "#eeeeee",
          }}
        >
          <SeriesHeader
            style={{
              padding: 16,
              borderBottomWidth: 1,
              borderBottomColor: "#f5f5f5",
            }}
          >
            <View
              style={{
                flexDirection: "row",
                alignItems: "center",
              }}
            >
              <TeamLogo
                source={opponentTeam.logo}
                resizeMode="contain"
                style={{ width: 32, height: 32 }}
                fadeDuration={0} // 페이드 효과 제거
                defaultSource={opponentTeam.logo} // 기본 이미지로 동일 소스 사용
              />
              <View style={{ marginLeft: 12 }}>
                <Text
                  style={{
                    fontSize: 16,
                    fontWeight: "bold",
                    color: "#333",
                  }}
                >
                  vs {opponentTeam.name}
                </Text>
                <Text
                  style={{
                    fontSize: 13,
                    color: "#666",
                    marginTop: 2,
                  }}
                >
                  {match.dateRange} ({locationText})
                </Text>
              </View>
            </View>
            <ResultBadge
              style={{
                backgroundColor: badgeColor,
                paddingVertical: 6,
                paddingHorizontal: 12,
                borderRadius: 12,
              }}
            >
              <ResultText
                style={{
                  color: badgeTextColor,
                  fontSize: 13,
                  fontWeight: "600",
                }}
              >
                {isCurrentSeries ? "진행 중" : match.result}
              </ResultText>
            </ResultBadge>
          </SeriesHeader>

          <DayRowContainer style={{ padding: 12 }}>
            {match.days.map((day, index) => {
              // 경기 상태에 따른 색상 및 라벨 설정
              let statusLabel = "";
              let statusColor = "#333";
              let badgeBgColor = "transparent";

              switch (day.status) {
                case "win":
                  statusLabel = "승";
                  statusColor = "#f44336";
                  badgeBgColor = "rgba(244, 67, 54, 0.2)";
                  break;
                case "lose":
                  statusLabel = "패";
                  statusColor = "#2196f3";
                  badgeBgColor = "rgba(33, 150, 243, 0.2)";
                  break;
                case "draw":
                  statusLabel = "무";
                  statusColor = "#4caf50";
                  badgeBgColor = "rgba(76, 175, 80, 0.2)";
                  break;
                case "cancelled":
                  statusLabel = "취소";
                  statusColor = "#9e9e9e";
                  badgeBgColor = "rgba(158, 158, 158, 0.2)";
                  break;
                case "upcoming":
                  statusLabel = "예정";
                  statusColor = "#9c27b0";
                  badgeBgColor = "rgba(156, 39, 176, 0.2)";
                  break;
              }

              // 배경색 설정
              const bgColor =
                day.status === "win"
                  ? "#f4f9ff"
                  : day.status === "lose"
                  ? "#fff0f0"
                  : "#f9f9f9";

              // 텍스트 색상 설정
              const textColor =
                day.status === "win"
                  ? "#1588CF"
                  : day.status === "lose"
                  ? "#ff4444"
                  : "#666";

              return (
                <DayBox
                  key={index}
                  backgroundColor={bgColor}
                  style={{
                    flex: 1,
                    padding: 14,
                    margin: 4,
                    borderRadius: 12,
                    alignItems: "center",
                  }}
                >
                  <DayText
                    style={{
                      color: "#666",
                      fontSize: 14,
                      marginBottom: 6,
                    }}
                  >
                    {day.date}
                  </DayText>

                  {/* 경기 상태 라벨 */}
                  {statusLabel && (
                    <View
                      style={{
                        paddingHorizontal: 8,
                        paddingVertical: 2,
                        borderRadius: 10,
                        backgroundColor: badgeBgColor,
                        marginBottom: 4,
                      }}
                    >
                      <Text
                        style={{
                          fontSize: 12,
                          fontWeight: "bold",
                          color: statusColor,
                        }}
                      >
                        {statusLabel}
                      </Text>
                    </View>
                  )}

                  {/* 금액 */}
                  <AmountText
                    color={textColor}
                    style={{
                      fontSize: 15,
                      fontWeight: "600",
                    }}
                  >
                    {formatAmount(day.amount)}
                  </AmountText>
                </DayBox>
              );
            })}
          </DayRowContainer>

          <TotalContainer
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              padding: 16,
              borderTopWidth: 1,
              borderTopColor: "#f0f0f0",
              backgroundColor: "#fcfcfc",
            }}
          >
            <TotalLabel style={{ fontSize: 14, color: "#666" }}>
              총 적립액
            </TotalLabel>
            <TotalAmount
              style={{
                fontSize: 16,
                fontWeight: "bold",
                color: "#1588CF",
              }}
            >
              {formatAmount(match.totalAmount)}
            </TotalAmount>
          </TotalContainer>
        </SeriesCard>
      );
    },
    (prevProps, nextProps) => {
      // id가 같으면 리렌더링하지 않음 (최적화)
      return prevProps.match.id === nextProps.match.id;
    }
  );

  // 캘린더 뷰 렌더링
  const renderCalendarView = () => (
    <>
      <CalendarCard width={width}>
        {isLoading ? (
          <View
            style={{
              padding: 20,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text>경기 일정 로딩 중...</Text>
          </View>
        ) : error ? (
          <View
            style={{
              padding: 20,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text>경기 일정을 불러오는데 실패했습니다.</Text>
          </View>
        ) : (
          renderCustomCalendar()
        )}
      </CalendarCard>

      {/* 선택한 날짜의 경기 상세 정보 */}
      {selectedFixture && <FixtureDetailComponent fixture={selectedFixture} />}

      {/* 3연전 일정 카드 - useMemo로 최적화 */}
      {useMemo(
        () => (
          <Card width={width}>
            <CardHeader width={width}>
              <CardTitle width={width}>3연전 일정</CardTitle>
            </CardHeader>
            <CardContent width={width} style={{ padding: 8 }}>
              {isSeriesLoading ? (
                <View style={{ padding: 20, alignItems: "center" }}>
                  <Text>3연전 정보 로딩 중...</Text>
                </View>
              ) : seriesMatches.length > 0 ? (
                seriesMatches.map((match) => (
                  <SeriesMatchCard key={match.id} match={match} />
                ))
              ) : (
                <View style={{ padding: 20, alignItems: "center" }}>
                  <Text>표시할 3연전 정보가 없습니다.</Text>
                </View>
              )}
            </CardContent>
          </Card>
        ),
        [isSeriesLoading, seriesMatches, width]
      )}
    </>
  );

  // 리스트 뷰 렌더링
  const renderListView = () => (
    <Card width={width}>
      <CardHeader width={width}>
        <CardTitle width={width}>적금 상세 내역</CardTitle>
      </CardHeader>

      {/* 월 이동 네비게이션 */}
      <ListMonthNavigator>
        <TouchableOpacity onPress={() => moveMonth(-1)}>
          <Ionicons name="chevron-back" size={24} color="#666" />
        </TouchableOpacity>

        <ListMonthTitle>
          {`${currentMonth.getFullYear()}년 ${currentMonth.getMonth() + 1}월`}
        </ListMonthTitle>

        <TouchableOpacity onPress={() => moveMonth(1)}>
          <Ionicons name="chevron-forward" size={24} color="#666" />
        </TouchableOpacity>
      </ListMonthNavigator>

      {/* 거래 내역 목록 */}
      <FlatList
        data={transactionItems}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => handleTransactionPress(item.id)}>
            <View>
              <TransactionHeader>
                {/* 좌측: 팀 정보와 날짜 */}
                <TeamInfoContainer>
                  <Text style={{ fontWeight: "bold", marginRight: 5 }}>vs</Text>
                  <Image
                    source={getTeamLogo(item.opponent)}
                    style={{ width: 28, height: 28, marginRight: 10 }}
                    fadeDuration={0} // 페이드 효과 제거
                  />
                  <Text style={{ color: "#666", fontSize: 14 }}>
                    {item.date}
                  </Text>
                </TeamInfoContainer>

                {/* 우측: 금액 */}
                <TransactionAmountText>
                  +{item.amount.toLocaleString()}원
                </TransactionAmountText>
              </TransactionHeader>

              {/* 설명 텍스트 */}
              <TransactionDescription>
                <DescriptionText>{item.description}</DescriptionText>
                <WinsText>{item.wins}개 획득</WinsText>
              </TransactionDescription>
            </View>
          </TouchableOpacity>
        )}
        contentContainerStyle={{ paddingBottom: 20 }}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={{ padding: 20, alignItems: "center" }}>
            <Text>해당 월의 거래 내역이 없습니다.</Text>
          </View>
        }
      />
    </Card>
  );

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <HeaderTitle width={width}>적금 내역</HeaderTitle>
          <HeaderRight>
            <IconButton
              isActive={viewMode === "calendar"}
              onPress={() => setViewMode("calendar")}
            >
              <Ionicons name="calendar" size={24} color="white" />
            </IconButton>
            <IconButton
              isActive={viewMode === "list"}
              onPress={() => setViewMode("list")}
            >
              <Ionicons name="list" size={24} color="white" />
            </IconButton>
          </HeaderRight>
        </Header>

        <SafeAreaView style={{ flex: 1, paddingBottom: 60 }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{
              padding: width * 0.04,
              paddingBottom: 20,
            }}
          >
            {viewMode === "calendar" ? renderCalendarView() : renderListView()}
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default SavingsScreen;
