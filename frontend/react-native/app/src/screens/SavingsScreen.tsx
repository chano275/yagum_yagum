import React, { useState, useMemo, useEffect } from "react";
import {
  useWindowDimensions,
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  Text,
  Image,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import { Calendar } from "react-native-calendars";
import { Ionicons } from "@expo/vector-icons";
import { useTeam } from "@/context/TeamContext";
import { RouteProp } from "@react-navigation/native";
import { useRoute } from "@react-navigation/native";
import { useFocusEffect } from "@react-navigation/native";

// 동적 스타일링을 위한 인터페이스
interface StyledProps {
  width: number;
}

// 뷰 모드 타입
type ViewMode = "calendar" | "list";

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
}

// CustomDay 컴포넌트 props 타입
interface CustomDayProps {
  date: {
    dateString: string;
    day: number;
    month: number;
    year: number;
  };
  state: string;
  marking?: {
    gameResult?: "win" | "lose" | "draw";
    amount?: number | null;
    teamLogo?: any;
  };
  onPress?: (date: any) => void;
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

// CustomDay 컴포넌트
const CustomDay = ({ date, state, marking, onPress }: CustomDayProps) => {
  // 날짜가 현재 월에 속하지 않으면 회색 처리
  const isDisabled = state === "disabled";

  // 경기 결과에 따른 배경색 설정
  let bgColor = "transparent";
  let statusLabel = "";
  let amount = null;
  let teamLogo = null;

  if (marking) {
    // 경기 결과에 따른 스타일 설정
    if (marking.gameResult === "win") {
      bgColor = "#ffebee"; // 승리는 연한 빨강
      statusLabel = "승";
    } else if (marking.gameResult === "lose") {
      bgColor = "#e3f2fd"; // 패배는 연한 파랑
      statusLabel = "패";
    } else if (marking.gameResult === "draw") {
      bgColor = "#e8f5e9"; // 무승부는 연한 초록
      statusLabel = "무";
    }

    // 적금 금액과 팀 로고
    amount = marking.amount;
    teamLogo = marking.teamLogo;
  }

  // 오늘 날짜 강조
  const isToday = new Date().toISOString().split("T")[0] === date.dateString;
  const todayStyle = isToday
    ? {
        borderWidth: 1,
        borderColor: "#f44336",
      }
    : {};

  return (
    <TouchableOpacity
      onPress={() => onPress && onPress(date)}
      style={{
        backgroundColor: bgColor,
        width: "100%",
        height: 70, // 높이를 늘려서 추가 정보 표시
        alignItems: "center",
        justifyContent: "flex-start",
        paddingTop: 5,
        opacity: isDisabled ? 0.4 : 1,
        ...todayStyle,
      }}
    >
      {/* 날짜 표시 */}
      <Text
        style={{
          fontSize: 14,
          color: isDisabled ? "#ccc" : "#333",
        }}
      >
        {date.day}
      </Text>

      {/* 경기 결과 */}
      {statusLabel !== "" && (
        <Text
          style={{
            fontSize: 12,
            fontWeight: "bold",
            marginTop: 2,
            color:
              marking.gameResult === "win"
                ? "#f44336"
                : marking.gameResult === "lose"
                ? "#2196f3"
                : "#4caf50",
          }}
        >
          {statusLabel}
        </Text>
      )}

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
        {amount !== null && (
          <Text
            style={{
              fontSize: 10,
              fontWeight: "bold",
              color: "#666",
            }}
          >
            {amount.toLocaleString()}원
          </Text>
        )}

        {/* 팀 로고 */}
        {teamLogo && (
          <Image
            source={teamLogo}
            style={{
              width: 15,
              height: 15,
              marginLeft: 2,
              borderRadius: 8,
            }}
          />
        )}
      </View>
    </TouchableOpacity>
  );
};

// 3연전 시리즈 카드 컴포넌트
const SeriesMatchCard = ({ match }: { match: SeriesMatch }) => {
  // 금액 포맷
  const formatAmount = (amount: number | null): string => {
    if (amount === null) return "-";
    return `${amount.toLocaleString()}원`;
  };

  return (
    <SeriesCard>
      <SeriesHeader>
        <TeamVsContainer>
          <TeamLogo source={match.homeTeam.logo} resizeMode="contain" />
          <VsText>VS</VsText>
          <TeamLogo source={match.awayTeam.logo} resizeMode="contain" />
          <DateRangeText>{match.dateRange}</DateRangeText>
        </TeamVsContainer>
        <ResultBadge>
          <ResultText>{match.result}</ResultText>
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

// 메인 컴포넌트
const SavingsScreen = () => {
  const { teamColor } = useTeam();
  const route = useRoute(); // 네비게이션 라우트 정보 가져오기
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 네비게이션 파라미터 처리
  useEffect(() => {
    try {
      // 디버깅을 위한 로그 추가
      console.log("전체 라우트 객체:", route);

      if (route && route.params) {
        console.log("라우트 파라미터:", route.params);

        // params가 객체인지 확인하고 안전하게 접근
        if (typeof route.params === "object") {
          // params 객체의 구조를 확인
          const params = route.params;
          console.log("params 내용:", params);

          // viewMode 속성이 있는지 확인
          if ("viewMode" in params) {
            const mode = params.viewMode;
            console.log("viewMode 값:", mode);

            if (mode === "list" || mode === "calendar") {
              setViewMode(mode);
            }
          } else {
            // 중첩된 params 객체 확인 (React Navigation 5 이상)
            if (
              params.params &&
              typeof params.params === "object" &&
              "viewMode" in params.params
            ) {
              const mode = params.params.viewMode;
              if (mode === "list" || mode === "calendar") {
                setViewMode(mode);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Navigation params error:", error);
    }
  }, [route?.params]);

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

  // 팀 로고 임포트 (실제 로고로 교체 필요)
  const teamLogos = {
    NC: require("../../assets/icon.png"),
    DOOSAN: require("../../assets/icon.png"),
    SAMSUNG: require("../../assets/icon.png"),
    LOTTE: require("../../assets/icon.png"),
    KIA: require("../../assets/icon.png"),
  };

  // 캘린더 데이터 - 실제 데이터로 교체 필요
  const calendarData = {
    "2025-03-09": {
      gameResult: "win",
      amount: 3000,
      teamLogo: teamLogos.DOOSAN,
    },
    "2025-03-10": {
      gameResult: "lose",
      amount: 0,
      teamLogo: teamLogos.DOOSAN,
    },
    "2025-03-11": {
      gameResult: "win",
      amount: 2000,
      teamLogo: teamLogos.KIA,
    },
    "2025-03-12": {
      gameResult: "win",
      amount: 15000,
      teamLogo: teamLogos.KIA,
    },
    "2025-03-13": {
      gameResult: "draw",
      amount: 1000,
      teamLogo: teamLogos.SAMSUNG,
    },
    "2025-03-14": {
      gameResult: "lose",
      amount: 0,
      teamLogo: teamLogos.SAMSUNG,
    },
    "2025-03-15": {
      gameResult: "win",
      amount: 3000,
      teamLogo: teamLogos.SAMSUNG,
    },
    "2025-03-16": {
      gameResult: "win",
      amount: 2000,
      teamLogo: teamLogos.LOTTE,
    },
    "2025-03-19": {
      gameResult: "lose",
      amount: 0,
      teamLogo: teamLogos.LOTTE,
    },
    "2025-03-28": {
      gameResult: "win",
      amount: 3000,
      teamLogo: teamLogos.NC,
    },
    "2025-03-29": {
      gameResult: "win",
      amount: 5000,
      teamLogo: teamLogos.NC,
    },
    "2025-03-30": {
      gameResult: "win",
      amount: 3000,
      teamLogo: teamLogos.NC,
    },
    "2025-03-31": {
      gameResult: "win",
      amount: 3000,
      teamLogo: teamLogos.NC,
    },
  };

  // 뷰 모드 상태 (캘린더 또는 리스트)
  const [viewMode, setViewMode] = useState<ViewMode>("calendar");
  // 현재 선택된 날짜 상태
  const [selectedDate, setSelectedDate] = useState("2025-03-28");

  // 3연전 시리즈 데이터 (이미지와 일치하도록 구성)
  const seriesMatches: SeriesMatch[] = [
    {
      id: "1",
      homeTeam: {
        name: "LIONS",
        logo: require("../../assets/icon.png"), // 실제 사용 시 팀 로고로 교체 필요
      },
      awayTeam: {
        name: "TWINS",
        logo: require("../../assets/icon.png"), // 실제 사용 시 팀 로고로 교체 필요
      },
      dateRange: "3/11 ~ 3/12",
      result: "1승 1패",
      days: [
        { date: "3/11", amount: 2000 },
        { date: "3/12", amount: 15000 },
      ],
      totalAmount: 17000,
    },
    {
      id: "2",
      homeTeam: {
        name: "LIONS",
        logo: require("../../assets/icon.png"),
      },
      awayTeam: {
        name: "BEARS",
        logo: require("../../assets/icon.png"),
      },
      dateRange: "3/8 ~ 3/9",
      result: "0승 1패",
      days: [
        { date: "3/8", amount: 3000 },
        { date: "3/9", amount: null },
      ],
      totalAmount: 3000,
    },
    {
      id: "3",
      homeTeam: {
        name: "LIONS",
        logo: require("../../assets/icon.png"),
      },
      awayTeam: {
        name: "WIZ",
        logo: require("../../assets/icon.png"),
      },
      dateRange: "예정된 경기",
      result: "-",
      days: [
        { date: "-", amount: null },
        { date: "-", amount: null },
        { date: "-", amount: null },
      ],
      totalAmount: 0,
    },
  ];

  // 캘린더 뷰 렌더링
  const renderCalendarView = () => (
    <>
      <CalendarCard width={width}>
        <Calendar
          current={"2025-03-01"}
          onDayPress={(day) => setSelectedDate(day.dateString)}
          monthFormat={"yyyy년 MM월"}
          dayComponent={({ date, state }) => (
            <CustomDay
              date={date}
              state={state}
              marking={calendarData[date.dateString]}
              onPress={(selectedDate) =>
                setSelectedDate(selectedDate.dateString)
              }
            />
          )}
          theme={{
            backgroundColor: "#ffffff",
            calendarBackground: "#ffffff",
            textSectionTitleColor: "#b6c1cd",
            selectedDayBackgroundColor: teamColor.primary,
            selectedDayTextColor: "#ffffff",
            todayTextColor: teamColor.primary,
            dayTextColor: "#2d4150",
            textDisabledColor: "#d9e1e8",
            arrowColor: teamColor.primary,
            monthTextColor: teamColor.primary,
            indicatorColor: teamColor.primary,
            textDayHeaderFontWeight: "600",
          }}
        />
      </CalendarCard>

      {/* 3연전 일정 카드 */}
      <Card width={width}>
        <CardHeader width={width}>
          <CardTitle width={width}>3연전 일정</CardTitle>
        </CardHeader>
        <CardContent width={width} style={{ padding: 8 }}>
          {seriesMatches.map((match) => (
            <SeriesMatchCard key={match.id} match={match} />
          ))}
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
      <CardContent width={width}>{/* 리스트 뷰 내용 */}</CardContent>
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
