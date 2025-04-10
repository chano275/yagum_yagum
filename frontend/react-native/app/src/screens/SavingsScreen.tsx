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
    date: string;      // M/D 형식 (화면 표시용)
    fullDate: string;  // YYYY-MM-DD 형식 (gameResults 조회용)
    amount: number | null;
    status: GameStatus;
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
}

// 경기 결과 응답 타입 정의
interface GameResultResponse {
  game_date: string;
  result: string;
  opponent_team_name: string;
  score: string;
  is_home: boolean;
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

// 경기 결과별 색상 정의
const RESULT_COLORS = {
  win: {
    text: '#155724',
    badge: '#D4EDDA',
    background: '#D4EDDA'
  },
  lose: {
    text: '#721C24',
    badge: '#F8D7DA',
    background: '#F8D7DA'
  },
  draw: {
    text: '#0C5460',
    badge: '#D1ECF1',
    background: '#D1ECF1'
  },
  cancelled: {
    text: '#6C757D',
    badge: '#EFEFEF',
    background: '#EFEFEF'
  },
  upcoming: {
    text: '#666666',
    badge: 'transparent',
    background: '#f9f9f9'
  }
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
  height: 68px;
  align-items: center;
  justify-content: space-between;
  padding: 4px 2px 3px 2px;
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

const TeamLogo = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.06}px;
  height: ${({ width }) => width * 0.06}px;
  margin-horizontal: ${({ width }) => width * 0.015}px;
  resize-mode: contain;
`;

const LogoContainer = styled.View`
  align-items: center;
  justify-content: center;
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
  padding: 14px;
  margin: 4px;
  border-radius: 12px;
  align-items: center;
  background-color: ${props => props.backgroundColor};
`;

const DayText = styled.Text`
  color: #666;
  font-size: 14px;
  margin-bottom: 6px;
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
  background-color: white;
  border-radius: 12px;
  margin-bottom: 12px;
  border-width: 1px;
  border-color: #eeeeee;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.06);
  `}
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
  padding: 0 16px 16px 16px;
`;

const DescriptionText = styled.Text`
  font-size: 14px;
  color: #333;
`;

const DateContainer = styled.View`
  background-color: #f9f9f9;
  padding: 12px 16px;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
  border-top-width: 1px;
  border-top-color: #eeeeee;
`;

const DateText = styled.Text`
  font-size: 13px;
  color: #666;
`;

const WinsText = styled.Text`
  font-size: 12px;
  color: #888;
  margin-top: 4px;
`;

type RootStackParamList = {
  TransactionDetail: { id: string };
  적금내역: { viewMode?: ViewMode };
};

interface RouteParams {
  viewMode?: ViewMode;
  params?: {
    viewMode?: ViewMode;
  };
}

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
  const [transactionItems, setTransactionItems] = useState<TransactionItem[]>([]);
  // 경기 결과를 저장할 상태 추가
  const [gameResults, setGameResults] = useState<{ [date: string]: GameResultResponse }>({});

  // 네비게이션 파라미터 처리
  useFocusEffect(
    React.useCallback(() => {
      const params = route.params as RouteParams;
      let mode: ViewMode = "calendar";

      if (params) {
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
  const identifySeriesMatches = async (games: GameSchedule[]): Promise<SeriesMatch[]> => {
    const seriesMatchesData: SeriesMatch[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (!games.length) return seriesMatchesData;

    // 적립 금액 데이터 가져오기
    let transfersData: { [date: string]: number } = {};
    try {
      const transfersResponse = await api.get('/api/account/transfers_log');
      transfersData = transfersResponse.data.reduce((acc: { [date: string]: number }, transfer: any) => {
        acc[transfer.DATE] = transfer.AMOUNT;
        return acc;
      }, {});
    } catch (error) {
      console.error('적립 금액 조회 실패:', error);
    }

    // 팀 ID 조합으로 그룹화
    const matchesByTeams: { [key: string]: GameSchedule[] } = {};

    games.forEach((game) => {
      const teams = [game.HOME_TEAM_ID, game.AWAY_TEAM_ID].sort().join("-");
      if (!matchesByTeams[teams]) {
        matchesByTeams[teams] = [];
      }
      matchesByTeams[teams].push(game);
    });

    // 각 팀 조합별로 연속 3경기(3연전) 찾기
    for (const teamGames of Object.values(matchesByTeams)) {
      teamGames.sort((a, b) => new Date(a.DATE).getTime() - new Date(b.DATE).getTime());

      for (let i = 0; i <= teamGames.length - 3; i++) {
        const potentialSeries = teamGames.slice(i, i + 3);
        const dates = potentialSeries.map((game) => game.DATE);

        if (isConsecutiveDates(dates)) {
          const startDate = formatShortDate(potentialSeries[0].DATE);
          const endDate = formatShortDate(potentialSeries[potentialSeries.length - 1].DATE);
          const firstGameDate = new Date(potentialSeries[0].DATE);
          firstGameDate.setHours(0, 0, 0, 0);
          const lastGameDate = new Date(potentialSeries[potentialSeries.length - 1].DATE);
          lastGameDate.setHours(0, 0, 0, 0);

          let seriesStatus: "current" | "past" | "upcoming" = "upcoming";
          if (lastGameDate < today) {
            seriesStatus = "past";
          } else if (firstGameDate <= today && today <= lastGameDate) {
            seriesStatus = "current";
          }

          // 각 경기별 상세 정보 - 실제 결과와 금액 반영
          const days = potentialSeries.map((game) => {
            const gameDate = new Date(game.DATE);
            gameDate.setHours(0, 0, 0, 0);
            
            let status: GameStatus = "upcoming";
            
            // 과거 경기인 경우에만 결과 반영
            if (gameDate < today) {
              const result = gameResults[game.DATE];
              if (result) {
                switch (result.result) {
                  case "승리":
                    status = "win";
                    break;
                  case "패배":
                    status = "lose";
                    break;
                  case "무승부":
                    status = "draw";
                    break;
                  case "취소":
                    status = "cancelled";
                    break;
                }
              }
            }

            return {
              date: formatShortDate(game.DATE),
              fullDate: game.DATE,
              amount: transfersData[game.DATE] || null,
              status
            };
          });

          // 총 적립액 계산 (실제 금액 기준)
          const totalAmount = days.reduce((sum, day) => sum + (day.amount || 0), 0);

          const homeTeam = {
            name: potentialSeries[0].home_team_name.split(" ")[0],
            logo: getTeamLogo(potentialSeries[0].home_team_name),
          };

          const awayTeam = {
            name: potentialSeries[0].away_team_name.split(" ")[0],
            logo: getTeamLogo(potentialSeries[0].away_team_name),
          };

          const isStartingToday =
            firstGameDate.getFullYear() === today.getFullYear() &&
            firstGameDate.getMonth() === today.getMonth() &&
            firstGameDate.getDate() === today.getDate();

          seriesMatchesData.push({
            id: `series-${seriesMatchesData.length + 1}`,
            homeTeam,
            awayTeam,
            dateRange: `${startDate} ~ ${endDate}`,
            result: seriesStatus === "past" ? "지난 경기" : "예정된 경기",
            days,
            totalAmount,
            status: seriesStatus,
            startTime: firstGameDate.getTime(),
            isStartingToday,
          });
        }
      }
    }

    // 우선순위에 따라 시리즈 정렬
    const currentSeries = seriesMatchesData
      .filter((series) => series.status === "current")
      .sort((a, b) => {
        if (a.isStartingToday && !b.isStartingToday) return -1;
        if (!a.isStartingToday && b.isStartingToday) return 1;
        return (b.startTime || 0) - (a.startTime || 0);
      });

    const pastSeries = seriesMatchesData
      .filter((series) => series.status === "past")
      .sort((a, b) => (b.startTime || 0) - (a.startTime || 0));

    const maxDisplayCount = 3;
    const result = [...currentSeries];
    const remainingSlots = Math.max(0, maxDisplayCount - result.length);
    if (remainingSlots > 0) {
      result.push(...pastSeries.slice(0, remainingSlots));
    }

    return result.slice(0, maxDisplayCount);
  };

  // 월별 거래 내역 데이터 가져오기
  const fetchTransactionsForMonth = async (month: Date) => {
    try {
      setIsLoading(true);
      // 데이터 요청 전에 기존 데이터 초기화
      setTransactionItems([]);
      
      // 현재 월 가져오기 (1-12)
      const currentMonth = month.getMonth() + 1;
      
      // 1. 거래 내역 API 호출
      const transferResponse = await api.get('/api/account/transfers_log', {
        params: { month: currentMonth }
      });

      // 2. 해당 월의 모든 날짜에 대한 경기 결과 가져오기
      const resultsResponse = await api.get('/api/game/user-team-results');
      const gameResults = resultsResponse.data.reduce((acc: { [key: string]: any }, result: any) => {
        acc[result.game_date] = result;
        return acc;
      }, {});
      
      // 3. API 응답을 TransactionItem 형식으로 변환
      const transactions: TransactionItem[] = transferResponse.data
        .filter((item: any) => {
          const dateObj = new Date(item.DATE);
          return dateObj.getMonth() + 1 === currentMonth;
        })
        .map((item: any) => {
          const dateObj = new Date(item.DATE);
          dateObj.setDate(dateObj.getDate() + 1);  // 날짜 +1
          const formattedDate = `적립일: ${dateObj.getFullYear()}.${dateObj.getMonth() + 1}.${dateObj.getDate()}`;
          
          const gameResult = gameResults[item.DATE];
          const opponentTeamName = gameResult?.opponent_team_name || "";
          
          return {
            id: item.DATE,
            opponent: opponentTeamName,
            date: formattedDate,
            description: item.TEXT,
            amount: item.AMOUNT
          };
        });
      
      setTransactionItems(transactions);
    } catch (error) {
      console.error("월별 거래 내역 조회 실패:", error);
      setTransactionItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  // API에서 경기 일정 가져오기
  useEffect(() => {
    const fetchGameSchedules = async () => {
      try {
        setIsLoading(true);
        setIsSeriesLoading(true);

        // 팀명으로 팀 ID 가져오기
        const teamId = getTeamIdByName(teamName || "");
        console.log("팀 ID로 경기일정 조회:", teamId);

        // 경기 결과 API 호출을 먼저 수행
        const resultsResponse = await api.get<GameResultResponse[]>('/api/game/user-team-results');
        
        // 경기 결과를 날짜별로 매핑
        const resultsMap = resultsResponse.data.reduce((acc, result) => {
          acc[result.game_date] = result;
          return acc;
        }, {} as { [date: string]: GameResultResponse });
        
        setGameResults(resultsMap);

        // 경기 일정 API 호출
        const scheduleResponse = await api.get(`/api/game/schedule/team/${teamId}`);

        if (scheduleResponse.status === 200 && Array.isArray(scheduleResponse.data)) {
          console.log(`경기 일정 ${scheduleResponse.data.length}개 조회 성공`);
          setGameSchedules(scheduleResponse.data);
          const seriesData = await identifySeriesMatches(scheduleResponse.data);
          setSeriesMatches(seriesData);
        } else {
          throw new Error("API 응답 형식이 올바르지 않습니다");
        }
      } catch (err) {
        console.error("경기 일정 조회 실패:", err);
        setError(err instanceof Error ? err : new Error("알 수 없는 오류"));
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
  }, [teamName]);

  // 거래 내역 초기 로드
  useEffect(() => {
    fetchTransactionsForMonth(currentMonth);
  }, []);

  // 날짜별 경기 일정 및 마킹 데이터 생성
  const markedDates = useMemo(() => {
    if (isLoading || !gameSchedules.length) return {};

    const markingsData: { [date: string]: MarkingData } = {};
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    gameSchedules.forEach((game) => {
      const isHomeTeam = game.HOME_TEAM_ID === getTeamIdByName(teamName);
      const opponentTeam = isHomeTeam ? game.away_team_name : game.home_team_name;
      const gameDate = new Date(game.DATE);
      gameDate.setHours(0, 0, 0, 0);

      // 경기 결과 확인
      const gameResult = gameResults[game.DATE];
      let status: GameStatus = "upcoming";  // 기본값을 'upcoming'으로 설정
      
      // 오늘 포함 미래 경기는 무조건 upcoming
      if (gameDate >= today) {
        status = "upcoming";
      }
      // 과거 경기만 결과 반영
      else if (gameResult) {
        switch (gameResult.result) {
          case "승리":
            status = "win";
            break;
          case "패배":
            status = "lose";
            break;
          case "무승부":
            status = "draw";
            break;
          case "취소":
            status = "cancelled";
            break;
          default:
            status = "upcoming";
        }
      }

      const gameWithStatus = {
        ...game,
        status,
        amount: null,
      };

      markingsData[game.DATE] = {
        gameResult: status,
        amount: null,
        teamLogo: getTeamLogo(opponentTeam),
        fixture: gameWithStatus,
      };
    });

    return markingsData;
  }, [gameSchedules, teamName, gameResults]);

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

  // 날짜 셀 컴포넌트 (최적화를 위해 분리)
  const DayCellComponent = React.memo(({ day, setSelectedDate, teamColor }: { 
    day: CalendarDay, 
    setSelectedDate: (date: string) => void, 
    teamColor: string 
  }) => {
    let statusLabel = "";
    let statusColor = "#333";
    let badgeBgColor = "transparent";
    let cellBgColor = "transparent";

    if (day.marking?.gameResult) {
      const { gameResult } = day.marking;
      switch (gameResult) {
        case "win":
          statusLabel = "승";
          statusColor = RESULT_COLORS.win.text;
          badgeBgColor = RESULT_COLORS.win.badge;
          cellBgColor = RESULT_COLORS.win.background;
          break;
        case "lose":
          statusLabel = "패";
          statusColor = RESULT_COLORS.lose.text;
          badgeBgColor = RESULT_COLORS.lose.badge;
          cellBgColor = RESULT_COLORS.lose.background;
          break;
        case "draw":
          statusLabel = "무";
          statusColor = RESULT_COLORS.draw.text;
          badgeBgColor = RESULT_COLORS.draw.badge;
          cellBgColor = RESULT_COLORS.draw.background;
          break;
        case "cancelled":
          statusLabel = "취소";
          statusColor = RESULT_COLORS.cancelled.text;
          badgeBgColor = RESULT_COLORS.cancelled.badge;
          cellBgColor = RESULT_COLORS.cancelled.background;
          break;
      }
    }

    // 선택된 날짜 스타일
    if (day.isSelected) {
      cellBgColor = day.marking ? cellBgColor : "#f0f0f0";
    }

    return (
      <DayCell
        key={day.dateString}
        onPress={() => setSelectedDate(day.dateString)}
        isToday={day.isToday}
        isSelected={day.isSelected}
        isCurrentMonth={day.isCurrentMonth}
        backgroundColor={cellBgColor}
        teamColor={teamColor}
      >
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
              color: day.isCurrentMonth ? statusColor : "#ccc",
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

        <View
          style={{
            alignItems: "center",
            justifyContent: "flex-end",
            marginTop: -4,
            marginBottom: 2,
            height: 32,
          }}
        >
          {day.marking?.amount !== null && day.marking?.amount !== undefined && (
            <Text
              style={{
                fontSize: 10,
                fontWeight: "bold",
                color: statusColor,
                marginBottom: 1,
              }}
            >
              {day.marking.amount.toLocaleString()}원
            </Text>
          )}

          {day.marking?.teamLogo && (
            <Image
              source={day.marking.teamLogo}
              style={{
                width: 28,
                height: 28,
              }}
              resizeMode="contain"
              fadeDuration={0}
            />
          )}
        </View>
      </DayCell>
    );
  }, (prevProps, nextProps) => {
    // 최적화를 위한 비교 함수
    const prevDay = prevProps.day;
    const nextDay = nextProps.day;
    
    // 날짜가 다르면 리렌더
    if (prevDay.dateString !== nextDay.dateString) {
      return false;
    }
    
    // 선택 상태가 변경되면 리렌더
    if (prevDay.isSelected !== nextDay.isSelected) {
      return false;
    }
    
    // 마킹 데이터가 둘 다 없으면 동일함
    if (!prevDay.marking && !nextDay.marking) {
      return true;
    }
    
    // 마킹 데이터 중 하나만 있으면 다름
    if (!prevDay.marking || !nextDay.marking) {
      return false;
    }
    
    // 경기 결과가 변경되면 리렌더
    return prevDay.marking.gameResult === nextDay.marking.gameResult;
  });

  // 날짜 셀 렌더링 함수 - 최적화된 컴포넌트 사용
  const renderDayCell = (day: CalendarDay) => {
    return (
      <DayCellComponent 
        key={day.dateString}
        day={day} 
        setSelectedDate={setSelectedDate} 
        teamColor={teamColor.primary}
      />
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
  const FixtureDetailComponent = ({ fixture }: { fixture: GameSchedule | null }) => {
    // 초기 gameResult 값을 미리 설정
    const initialResult = fixture ? gameResults[fixture.DATE] || null : null;
    const [resultData, setResultData] = useState<GameResultResponse | null>(initialResult);

    useEffect(() => {
      const fetchGameResult = async () => {
        if (!fixture) return;
        
        // 미래 경기 체크
        const gameDate = new Date(fixture.DATE);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        gameDate.setHours(0, 0, 0, 0);

        if (gameDate > today) {
          setResultData(null);
          return;
        }

        // 이미 gameResults 객체에 결과가 있는지 확인
        if (gameResults[fixture.DATE]) {
          setResultData(gameResults[fixture.DATE]);
          return;
        }
        
        try {
          // 필요한 경우에만 API 호출
          const response = await api.get<GameResultResponse[]>('/api/game/user-team-results', {
            params: {
              end_date: fixture.DATE
            }
          });
          
          const result = response.data.find(
            (result) => result.game_date === fixture.DATE
          );
          
          setResultData(result || null);
        } catch (error) {
          console.error('경기 결과 조회 실패:', error);
          setResultData(null);
        }
      };

      // 초기값이 없는 경우에만 데이터 불러오기
      if (!initialResult) {
        fetchGameResult();
      }
    }, [fixture, initialResult]);

    if (!fixture) return null;

    // 상대팀 정보만 구하기
    const isHomeTeam = fixture.HOME_TEAM_ID === getTeamIdByName(teamName || "");
    const opponent = isHomeTeam ? fixture.away_team_name : fixture.home_team_name;
    const opponentLogo = getTeamLogo(opponent);
    const locationText = isHomeTeam ? "홈경기" : "원정경기";

    // 경기 상태 텍스트
    const getGameStatusText = () => {
      const gameDate = new Date(fixture.DATE);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      gameDate.setHours(0, 0, 0, 0);

      // 오늘 포함 미래 경기
      if (gameDate >= today) {
        return "예정";
      }

      // 과거 경기 - gameResults에서 직접 확인하여 컴포넌트 상태에 의존하지 않도록 함
      const cachedResult = gameResults[fixture.DATE] || resultData;
      if (cachedResult) {
        return `${cachedResult.result} (${cachedResult.score})`;
      }

      return "예정";
    };

    // 결과에 따른 색상 가져오기
    const getResultColor = (): string => {
      const cachedResult = gameResults[fixture.DATE] || resultData;
      if (!cachedResult) return "#333";
      
      switch (cachedResult.result) {
        case "승리": return "#ff5555";
        case "패배": return "#2196f3";
        default: return "#333";
      }
    };

    return (
      <Card width={width} style={{ borderRadius: 16, overflow: "hidden" }}>
        <CardHeader width={width} style={{ backgroundColor: "#f8f8f8", borderBottomWidth: 0 }}>
          <CardTitle width={width}>경기 상세 정보</CardTitle>
        </CardHeader>
        <CardContent width={width} style={{ padding: 16 }}>
          <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 16 }}>
            <Image source={opponentLogo} style={{ width: 36, height: 36, marginRight: 12 }} resizeMode="contain" />
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 18, fontWeight: "bold", color: "#333" }}>vs {opponent}</Text>
              <Text style={{ fontSize: 14, color: "#666", marginTop: 4 }}>{locationText}</Text>
            </View>
          </View>

          <View style={{ flexDirection: "row", backgroundColor: "#f8f8f8", padding: 12, borderRadius: 12, marginBottom: 16 }}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 13, color: "#888" }}>일시</Text>
              <Text style={{ fontSize: 15, fontWeight: "500", marginTop: 4 }}>{fixture.DATE}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 13, color: "#888" }}>상태</Text>
              <Text style={{
                fontSize: 15,
                fontWeight: "600",
                marginTop: 4,
                color: getResultColor()
              }}>
                {getGameStatusText()}
              </Text>
            </View>
          </View>

          {fixture.amount !== null && fixture.amount !== undefined && (
            <View style={{ backgroundColor: "#f0f8ff", padding: 12, borderRadius: 12, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
              <Text style={{ fontSize: 15, color: "#333" }}>적립액</Text>
              <Text style={{ fontSize: 17, fontWeight: "bold", color: teamColor.primary }}>{fixture.amount.toLocaleString()}원</Text>
            </View>
          )}
        </CardContent>
      </Card>
    );
  };

  // 3연전 시리즈 카드 컴포넌트
  const SeriesMatchCard = ({ match }: { match: SeriesMatch }) => {
    const { width } = useWindowDimensions();
    const formatAmount = (amount: number | null): string => {
      if (amount === null) return "-";
      return `${amount.toLocaleString()}원`;
    };

    const isMyTeamHome = match.homeTeam.name.includes(teamName?.split(" ")[0] || "");
    const opponentTeam = isMyTeamHome ? match.awayTeam : match.homeTeam;
    const locationText = isMyTeamHome ? "홈" : "원정";

    const isCurrentSeries = match.status === "current";
    const badgeColor = isCurrentSeries ? "#1588CF" : "#e8f4ff";
    const badgeTextColor = isCurrentSeries ? "white" : "#0066cc";

    // 경기 결과 표시 함수
    const getGameStatus = (date: string, fullDate: string): GameStatus => {
      const gameDate = new Date(fullDate);  // fullDate(YYYY-MM-DD) 사용
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      gameDate.setHours(0, 0, 0, 0);

      if (gameDate > today) return "upcoming";

      const result = gameResults[fullDate];  // fullDate로 결과 조회
      if (!result) return "upcoming";

      switch (result.result) {
        case "승리": return "win";
        case "패배": return "lose";
        case "무승부": return "draw";
        case "취소": return "cancelled";
        default: return "upcoming";
      }
    };

    return (
      <SeriesCard style={{ borderRadius: 16, marginBottom: 16, borderColor: "#eeeeee" }}>
        <SeriesHeader style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: "#f5f5f5" }}>
          <View style={{ flexDirection: "row", alignItems: "center" }}>
            <TeamLogo 
              source={opponentTeam.logo} 
              width={width}
              resizeMode="contain" 
              style={{ width: 32, height: 32 }} 
            />
            <View style={{ marginLeft: 12 }}>
              <Text style={{ fontSize: 16, fontWeight: "bold", color: "#333" }}>vs {opponentTeam.name}</Text>
              <Text style={{ fontSize: 13, color: "#666", marginTop: 2 }}>{match.dateRange} ({locationText})</Text>
            </View>
          </View>
          <ResultBadge style={{ backgroundColor: badgeColor, paddingVertical: 6, paddingHorizontal: 12, borderRadius: 12 }}>
            <ResultText style={{ color: badgeTextColor, fontSize: 13, fontWeight: "600" }}>
              {isCurrentSeries ? "진행 중" : match.result}
            </ResultText>
          </ResultBadge>
        </SeriesHeader>

        <DayRowContainer style={{ padding: 12 }}>
          {match.days.map((day, index) => {
            const gameStatus = getGameStatus(day.date, day.fullDate);
            const resultStyle = RESULT_COLORS[gameStatus];

            return (
              <DayBox key={index} backgroundColor={resultStyle.background} style={{ flex: 1, padding: 14, margin: 4, borderRadius: 12, alignItems: "center" }}>
                <DayText style={{ color: "#666", fontSize: 14, marginBottom: 6 }}>{day.date}</DayText>
                <View style={{ paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10, backgroundColor: resultStyle.badge, marginBottom: 4 }}>
                  <Text style={{ fontSize: 12, fontWeight: "bold", color: resultStyle.text }}>
                    {gameStatus === "upcoming" ? "-" :
                     gameStatus === "win" ? "승" :
                     gameStatus === "lose" ? "패" :
                     gameStatus === "draw" ? "무" : "취소"}
                  </Text>
                </View>
                <Text style={{ fontSize: 15, fontWeight: "600", color: resultStyle.text }}>
                  {formatAmount(day.amount)}
                </Text>
              </DayBox>
            );
          })}
        </DayRowContainer>

        <TotalContainer style={{ padding: 16, borderTopWidth: 1, borderTopColor: "#f0f0f0" }}>
          <TotalLabel style={{ fontSize: 14, color: "#666" }}>총 적립액</TotalLabel>
          <TotalAmount style={{ fontSize: 16, fontWeight: "bold", color: "#1588CF" }}>
            {formatAmount(match.totalAmount)}
          </TotalAmount>
        </TotalContainer>
      </SeriesCard>
    );
  };

  // 리스트 뷰 렌더링 함수
  const renderListView = () => (
    <>
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
            <TransactionItem>
              <View>
                <TransactionHeader>
                  <TeamInfoContainer>
                    <Text style={{ fontWeight: "bold", marginRight: 5 }}>vs</Text>
                    <Image 
                      source={getTeamLogo(item.opponent)} 
                      style={{ width: 32, height: 32, marginRight: 10 }} 
                      resizeMode="contain"
                    />
                  </TeamInfoContainer>
                  <TransactionAmountText>
                    +{item.amount.toLocaleString()}원
                  </TransactionAmountText>
                </TransactionHeader>
                <TransactionDescription>
                  <DescriptionText numberOfLines={1} ellipsizeMode="tail">
                    {item.description}
                  </DescriptionText>
                </TransactionDescription>
              </View>
              <DateContainer>
                <DateText>{item.date}</DateText>
              </DateContainer>
            </TransactionItem>
          </TouchableOpacity>
        )}
        contentContainerStyle={{ padding: 16 }}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={{ padding: 20, alignItems: "center" }}>
            <Text>해당 월의 거래 내역이 없습니다.</Text>
          </View>
        }
      />
    </>
  );

  // 캘린더 뷰 렌더링
  const renderCalendarView = () => (
    <>
      <CalendarCard width={width}>
        {isLoading ? (
          <View style={{ padding: 20, alignItems: "center", justifyContent: "center" }}>
            <Text>경기 일정 로딩 중...</Text>
          </View>
        ) : error ? (
          <View style={{ padding: 20, alignItems: "center", justifyContent: "center" }}>
            <Text>경기 일정을 불러오는데 실패했습니다.</Text>
          </View>
        ) : (
          renderCustomCalendar()
        )}
      </CalendarCard>

      {/* 선택한 날짜의 경기 상세 정보 */}
      {selectedFixture && <FixtureDetailComponent fixture={selectedFixture} />}

      {/* 3연전 일정 카드 */}
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
    </>
  );

  // 팀 로고 사전 로드 (성능 최적화)
  useEffect(() => {
    // 이미지 캐싱을 위한 사전 로드
    const preloadTeamLogos = () => {
      // 모든 팀 로고 미리 로드
      Object.values(teamLogos).forEach(logo => {
        if (Platform.OS !== 'web') {
          const source = Image.resolveAssetSource(logo);
          if (source && source.uri) {
            Image.prefetch(source.uri).catch(() => {});
          }
        }
      });
    };
    
    preloadTeamLogos();
  }, []);

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <HeaderTitle width={width}>적금 내역</HeaderTitle>
          <HeaderRight>
            <IconButton isActive={viewMode === "calendar"} onPress={() => setViewMode("calendar")}>
              <Ionicons name="calendar" size={24} color="white" />
            </IconButton>
            <IconButton isActive={viewMode === "list"} onPress={() => setViewMode("list")}>
              <Ionicons name="list" size={24} color="white" />
            </IconButton>
          </HeaderRight>
        </Header>

        <SafeAreaView style={{ flex: 1, paddingBottom: 60 }}>
          <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false} contentContainerStyle={{ padding: width * 0.04, paddingBottom: 20 }}>
            {viewMode === "calendar" ? renderCalendarView() : renderListView()}
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default SavingsScreen;
