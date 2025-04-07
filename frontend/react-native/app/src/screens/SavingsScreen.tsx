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
import { useRoute } from "@react-navigation/native";
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
  }[];
  totalAmount: number;
  status?: "current" | "past" | "upcoming"; // 상태 추가
  startTime?: number; // 정렬용 시작 시간 추가
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
  padding-horizontal: 12px;
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
`;

const DayCell = styled.TouchableOpacity<{
  isToday: boolean;
  isSelected: boolean;
  isCurrentMonth: boolean;
  backgroundColor: string;
  teamColor: string;
}>`
  width: ${100 / 7}%;
  aspect-ratio: 1;
  align-items: center;
  justify-content: flex-start;
  padding-top: 5px;
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

const SavingsScreen = () => {
  const { teamColor, teamName } = useTeam();
  const route = useRoute();
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
    NC: require("../../assets/icon.png"),
    DOOSAN: require("../../assets/icon.png"),
    SAMSUNG: require("../../assets/icon.png"),
    LOTTE: require("../../assets/icon.png"),
    KIA: require("../../assets/icon.png"),
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
    const logoMap: { [key: string]: any } = {
      "KIA 타이거즈": teamLogos.KIA,
      "삼성 라이온즈": teamLogos.SAMSUNG,
      "LG 트윈스": teamLogos.NC, // 실제 로고로 교체 필요
      "두산 베어스": teamLogos.DOOSAN,
      "KT 위즈": teamLogos.NC, // 실제 로고로 교체 필요
      "SSG 랜더스": teamLogos.NC, // 실제 로고로 교체 필요
      "롯데 자이언츠": teamLogos.LOTTE,
      "한화 이글스": teamLogos.NC, // 실제 로고로 교체 필요
      "NC 다이노스": teamLogos.NC,
      "키움 히어로즈": teamLogos.NC, // 실제 로고로 교체 필요
    };
    return logoMap[teamName] || teamLogos.NC;
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
          const lastGameDate = new Date(
            potentialSeries[potentialSeries.length - 1].DATE
          );

          // 시리즈 상태 결정 (진행 중/과거/미래)
          let seriesStatus = "upcoming";
          if (lastGameDate < today) {
            seriesStatus = "past"; // 3연전이 모두 지난 경우
          } else if (firstGameDate <= today && today <= lastGameDate) {
            seriesStatus = "current"; // 3연전이 진행 중인 경우
          }

          // 모든 경기를 "upcoming"으로 설정 (무작위 값 제거)
          const gameStatuses: GameStatus[] = potentialSeries.map(
            () => "upcoming"
          );
          const result = "예정된 경기";

          // 각 경기별 상세 정보 (무작위 금액 생성 제거)
          const days = potentialSeries.map((game) => ({
            date: formatShortDate(game.DATE),
            amount: null,
          }));

          // 홈팀과 원정팀 결정
          const homeTeam = {
            name: potentialSeries[0].home_team_name.split(" ")[0],
            logo: getTeamLogo(potentialSeries[0].home_team_name),
          };

          const awayTeam = {
            name: potentialSeries[0].away_team_name.split(" ")[0],
            logo: getTeamLogo(potentialSeries[0].away_team_name),
          };

          // 시리즈 정보 추가
          allSeries.push({
            id: `series-${allSeries.length + 1}`,
            homeTeam,
            awayTeam,
            dateRange: `${startDate} ~ ${endDate}`,
            result,
            days,
            totalAmount: 0,
            status: seriesStatus, // 상태 정보 추가
            startTime: firstGameDate.getTime(), // 정렬을 위한 시작 시간 추가
          });
        }
      }
    });

    // 우선순위에 따라 시리즈 정렬 및 선택
    // 1. 현재 진행 중인 시리즈
    const currentSeries = allSeries
      .filter((series) => series.status === "current")
      .sort((a, b) => b.startTime - a.startTime);

    // 2. 과거 시리즈 (최신순)
    const pastSeries = allSeries
      .filter((series) => series.status === "past")
      .sort((a, b) => b.startTime - a.startTime);

    // 3. 결과 구성: 현재 진행 중 시리즈 + 과거 시리즈 (최대 2개)
    const result = [
      ...currentSeries.slice(0, 1), // 현재 진행 중인 시리즈 (최대 1개)
      ...pastSeries.slice(0, 2), // 과거 시리즈 (최대 2개)
    ];

    return result;
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
    // 경기 결과에 따른 배경색과 라벨 설정
    let bgColor = "transparent";
    let statusLabel = "";
    let statusColor = "#333";
    let badgeBgColor = "transparent";

    if (day.marking) {
      const { gameResult } = day.marking;

      switch (gameResult) {
        case "win":
          bgColor = "#ffebee";
          statusLabel = "승";
          statusColor = "#f44336";
          badgeBgColor = "rgba(244, 67, 54, 0.2)";
          break;
        case "lose":
          bgColor = "#e3f2fd";
          statusLabel = "패";
          statusColor = "#2196f3";
          badgeBgColor = "rgba(33, 150, 243, 0.2)";
          break;
        case "draw":
          bgColor = "#e8f5e9";
          statusLabel = "무";
          statusColor = "#4caf50";
          badgeBgColor = "rgba(76, 175, 80, 0.2)";
          break;
        case "cancelled":
          bgColor = "#f5f5f5";
          statusLabel = "취";
          statusColor = "#9e9e9e";
          badgeBgColor = "rgba(158, 158, 158, 0.2)";
          break;
        case "upcoming":
          bgColor = "#f3e5f5";
          statusLabel = "예";
          statusColor = "#9c27b0";
          badgeBgColor = "rgba(156, 39, 176, 0.2)";
          break;
      }
    }

    // 선택된 날짜 또는 오늘 날짜는 배경색 변경
    if (day.isSelected) {
      bgColor = day.marking ? bgColor : "#f0f0f0";
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
        {/* 날짜 표시 */}
        <Text
          style={{
            fontSize: 14,
            color: day.isCurrentMonth ? "#333" : "#ccc",
            fontWeight: day.isToday || day.isSelected ? "bold" : "normal",
          }}
        >
          {day.day}
        </Text>

        {/* 경기 결과 */}
        {statusLabel ? (
          <View
            style={{
              paddingHorizontal: 6,
              paddingVertical: 2,
              borderRadius: 10,
              backgroundColor: badgeBgColor,
              marginTop: 2,
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

        {/* 하단 영역: 금액과 로고 */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "center",
            marginTop: 3,
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
                width: 15,
                height: 15,
                marginLeft: 2,
                borderRadius: 8,
              }}
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

    const isHomeTeam = fixture.HOME_TEAM_ID === getTeamIdByName(teamName);
    const opponent = isHomeTeam
      ? fixture.away_team_name
      : fixture.home_team_name;

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
      <Card width={width}>
        <CardHeader width={width}>
          <CardTitle width={width}>경기 상세 정보</CardTitle>
        </CardHeader>
        <CardContent width={width}>
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 10,
            }}
          >
            <Image
              source={getTeamLogo(fixture.home_team_name)}
              style={{ width: 30, height: 30, marginRight: 10 }}
            />
            <Text style={{ flex: 1, fontSize: 16, fontWeight: "bold" }}>
              {fixture.home_team_name} VS {fixture.away_team_name}
            </Text>
            <Image
              source={getTeamLogo(fixture.away_team_name)}
              style={{ width: 30, height: 30 }}
            />
          </View>

          <View style={{ marginBottom: 5 }}>
            <Text style={{ fontSize: 14 }}>일시: {fixture.DATE}</Text>
          </View>

          <View style={{ marginBottom: 5 }}>
            <Text style={{ fontSize: 14 }}>
              상태: {getStatusText(fixture.status)}
            </Text>
          </View>

          {fixture.amount !== null && fixture.amount !== undefined && (
            <View style={{ marginTop: 5 }}>
              <Text
                style={{
                  fontSize: 14,
                  fontWeight: "bold",
                  color: teamColor.primary,
                }}
              >
                적립액: {fixture.amount.toLocaleString()}원
              </Text>
            </View>
          )}
        </CardContent>
      </Card>
    );
  };

  // 3연전 시리즈 카드 컴포넌트
  const SeriesMatchCard = ({ match }: { match: SeriesMatch }) => {
    // 금액 포맷
    const formatAmount = (amount: number | null): string => {
      if (amount === null) return "-";
      return `${amount.toLocaleString()}원`;
    };

    // 진행 중인 시리즈에 특별한 스타일 적용
    const isCurrentSeries = match.status === "current";
    const badgeColor = isCurrentSeries ? "#FF5722" : "#e8f4ff";
    const badgeTextColor = isCurrentSeries ? "white" : "#0066cc";

    return (
      <SeriesCard>
        <SeriesHeader>
          <TeamVsContainer>
            <TeamLogo source={match.homeTeam.logo} resizeMode="contain" />
            <VsText>VS</VsText>
            <TeamLogo source={match.awayTeam.logo} resizeMode="contain" />
            <DateRangeText>{match.dateRange}</DateRangeText>
          </TeamVsContainer>
          <ResultBadge style={{ backgroundColor: badgeColor }}>
            <ResultText style={{ color: badgeTextColor }}>
              {isCurrentSeries ? "진행 중" : match.result}
            </ResultText>
          </ResultBadge>
        </SeriesHeader>

        <DayRowContainer>
          {match.days.map((day, index) => {
            // 금액 유무와 날짜 위치에 따른 색상 설정
            const hasAmount = day.amount !== null;
            const isFirstDay = index === 0;
            const bgColor = hasAmount
              ? isFirstDay
                ? "#ffe8e8"
                : "#e8f9ee"
              : "#f5f5f5";
            const textColor = hasAmount
              ? isFirstDay
                ? "#ff5555"
                : "#00aa55"
              : "#999";

            return (
              <DayBox key={index} backgroundColor={bgColor}>
                <DayText>{day.date}</DayText>
                <AmountText color={textColor}>
                  {formatAmount(day.amount)}
                </AmountText>
              </DayBox>
            );
          })}
        </DayRowContainer>

        <TotalContainer>
          <TotalLabel>시리즈 총 적립액</TotalLabel>
          <TotalAmount>{formatAmount(match.totalAmount)}</TotalAmount>
        </TotalContainer>
      </SeriesCard>
    );
  };

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

  // 리스트 뷰 렌더링
  const renderListView = () => (
    <Card width={width}>
      <CardHeader width={width}>
        <CardTitle width={width}>적금 상세 내역</CardTitle>
      </CardHeader>
      <CardContent width={width}>
        <Text>적금 상세 내역을 준비 중입니다.</Text>
      </CardContent>
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
