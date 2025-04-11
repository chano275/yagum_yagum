import React, { useState, useEffect } from "react";
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
import { useTeam } from "@/context/TeamContext";
import { Ionicons } from "@expo/vector-icons";
import { api } from "@/api/axios"; // API 클라이언트 임포트
import { useNavigation } from "@react-navigation/native"; // useNavigation 임포트 추가
import { MaterialIcons } from "@expo/vector-icons";
import { theme } from "@/styles/theme";  // theme import 추가

// 동적 스타일링을 위한 인터페이스
interface StyledProps {
  width: number;
}

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// 주간 리포트 응답 타입 정의
interface WeeklyReport {
  DATE: string;
  WEEKLY_AMOUNT: number;
  LLM_CONTEXT: string | null;
  TEAM_RECORD: {
    WIN: number;
    LOSE: number;
    DRAW: number;
  };
  PREVIOUS_WEEK: number;
  CHANGE_PERCENTAGE: number;
  DAILY_SAVINGS: {
    [key: string]: number;
  };
  NEWS_SUMMATION: string;
}

// 막대 차트 데이터 타입 정의
interface BarChartData {
  labels: string[];
  datasets: {
    data: number[];
  }[];
}

// 도넛 차트 아이템 타입 정의
interface DonutChartItem {
  name: string;
  population: number;
  color: string;
}

// --- 스타일 컴포넌트 (기존과 동일) ---
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
  position: absolute;
  left: 0;
  right: 0;
  color: white;
  font-size: 20px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
  text-align: center;
`;

const BackButton = styled.TouchableOpacity`
  padding: 8px;
  z-index: 1;
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

const SummaryItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const SummaryLabel = styled.Text`
  font-size: 14px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const SummaryValue = styled.Text<{ teamColor?: string; positive?: boolean }>`
  font-size: 16px;
  font-weight: bold;
  color: ${(props) =>
    props.positive ? "#4CAF50" : props.teamColor ? props.teamColor : "#333"};
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ChartContainer = styled.View`
  align-items: center;
  margin-vertical: 10px;
`;

const LegendContainer = styled.View`
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 10px;
`;

const LegendItem = styled.View`
  flex-direction: row;
  align-items: center;
  margin-horizontal: 10px;
  margin-vertical: 5px;
`;

const LegendColor = styled.View<{ color: string }>`
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background-color: ${(props) => props.color};
  margin-right: 5px;
`;

const LegendText = styled.Text`
  font-size: 12px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const TeamStatItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const TeamStatLabel = styled.Text`
  font-size: 14px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const TeamStatValue = styled.Text<{ highlight?: boolean }>`
  font-size: 14px;
  font-weight: ${(props) => (props.highlight ? "bold" : "normal")};
  color: ${(props) => (props.highlight ? "#4CAF50" : "#333")};
  font-family: ${(props) => props.highlight ? props.theme.fonts.bold : props.theme.fonts.regular};
`;

const NewsItem = styled.TouchableOpacity`
  padding: 10px 0;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const NewsTitle = styled.Text`
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const NewsDate = styled.Text`
  font-size: 12px;
  color: #999;
  font-family: ${({ theme }) => theme.fonts.regular};
`;
// -----------------------------

// 막대 차트 컴포넌트 (기존과 동일)
const BarChartFallback = ({ 
  data, 
  width, 
  teamColor 
}: { 
  data: BarChartData; 
  width: number; 
  teamColor: string 
}) => {
  const maxValue =
    data.datasets[0].data.length > 0 ? Math.max(...data.datasets[0].data) : 1; // 데이터 없을 경우 대비

  return (
    <View style={{ width: width * 0.85, height: 220 }}>
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          height: 180,
          alignItems: "flex-end",
          borderBottomWidth: 1,
          borderBottomColor: "#ccc",
          paddingBottom: 5,
        }}
      >
        {data.labels.map((label: string, index: number) => {
          const value = data.datasets[0].data[index] ?? 0; // 데이터 없을 경우 0
          const barHeight = maxValue > 0 ? (value / maxValue) * 160 : 0; // 0으로 나누는 것 방지

          return (
            <View
              key={index}
              style={{ alignItems: "center", flex: 1, marginHorizontal: 2 }}
            >
              <Text style={{ 
                fontSize: 10, 
                color: "#999", 
                marginBottom: 2,
                fontFamily: theme.fonts.regular 
              }}>
                {value.toLocaleString()}원
              </Text>
              <View
                style={{
                  width: "80%", // 막대 너비 조정
                  height: barHeight,
                  backgroundColor: teamColor || "#007AFF", // 기본 색상 추가
                  borderTopLeftRadius: 4,
                  borderTopRightRadius: 4,
                }}
              />
              <Text style={{ 
                marginTop: 5, 
                fontSize: 12, 
                color: "#666",
                fontFamily: theme.fonts.regular 
              }}>
                {label}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
};

// 커스텀 도넛 차트 (기존과 동일)
const CustomDonutChart = ({ 
  data, 
  width 
}: { 
  data: DonutChartItem[]; 
  width: number 
}) => {
  const totalAmount = data.reduce(
    (sum: number, item: DonutChartItem) => sum + Math.round((item.population / 100) * 78500),
    0
  ); // 실제 금액 합계 계산
  // const total = data.reduce((sum, item) => sum + item.population, 0); // 퍼센트 합계는 100이 아닐 수 있음

  return (
    <View style={{ width: width * 0.85, alignItems: "center" }}>
      <View style={{ marginBottom: 20, alignItems: "center" }}>
        <Text style={{ 
          fontSize: 16, 
          fontWeight: "bold", 
          color: "#333",
          fontFamily: theme.fonts.bold 
        }}>
          적금 유형별 분석
        </Text>
      </View>

      <View
        style={{
          width: "100%",
          padding: 10,
          backgroundColor: "#f8f9fa",
          borderRadius: 8,
          marginBottom: 15,
        }}
      >
        {data.map((item: DonutChartItem, index: number) => {
          const amount = Math.round((item.population / 100) * 78500); // 금액 계산은 유지

          return (
            <View key={index} style={{ marginBottom: 12 }}>
              <View
                style={{
                  flexDirection: "row",
                  justifyContent: "space-between",
                  marginBottom: 4,
                }}
              >
                <View style={{ flexDirection: "row", alignItems: "center" }}>
                  <View
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: 6,
                      backgroundColor: item.color,
                      marginRight: 6,
                    }}
                  />
                  <Text style={{ 
                    fontWeight: "bold", 
                    color: "#333",
                    fontFamily: theme.fonts.bold 
                  }}>
                    {" "}
                    {item.name}{" "}
                  </Text>
                </View>
                <Text style={{ 
                  fontWeight: "bold", 
                  color: "#333",
                  fontFamily: theme.fonts.bold 
                }}>
                  {" "}
                  {item.population}%{" "}
                </Text>
              </View>
              <View
                style={{
                  height: 8,
                  backgroundColor: "#e9ecef",
                  borderRadius: 4,
                  overflow: "hidden",
                }}
              >
                <View
                  style={{
                    width: `${item.population}%`,
                    height: "100%",
                    backgroundColor: item.color,
                    borderRadius: 4,
                  }}
                />
              </View>
              <Text
                style={{
                  fontSize: 12,
                  color: "#666",
                  alignSelf: "flex-end",
                  marginTop: 2,
                  fontFamily: theme.fonts.regular
                }}
              >
                {amount.toLocaleString()}원
              </Text>
            </View>
          );
        })}
      </View>

      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          width: "100%",
          padding: 10,
          backgroundColor: "#e9ecef",
          borderRadius: 8,
        }}
      >
        <Text style={{ 
          fontWeight: "bold", 
          color: "#333",
          fontFamily: theme.fonts.bold 
        }}>총 적립액</Text>
        <Text style={{ 
          fontWeight: "bold", 
          color: "#1E3A8A",
          fontFamily: theme.fonts.bold 
        }}>
          {totalAmount.toLocaleString()}원
        </Text>
      </View>
    </View>
  );
};

// Navigation 타입 정의
interface NavigationProps {
  goBack: () => void;
}

const WeeklyReportScreen = ({ navigation }: { navigation: NavigationProps }) => {
  const {
    teamColor = { primary: "#007AFF" },
    teamName,
    currentTeam,
  } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  const [newsData, setNewsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklyReport | null>(null);

  useEffect(() => {
    const fetchWeeklyReport = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/report/weekly/');
        
        if (response.status === 200 && response.data) {
          setWeeklyData(response.data);
          
          // 뉴스 데이터 처리
          if (response.data.NEWS_SUMMATION) {
            const newsLines = response.data.NEWS_SUMMATION.split('\n')
              .map((line: string, index: number) => ({
                id: index + 1,
                title: line.startsWith('- ') ? line.substring(2).trim() : line.trim(),
                date: response.data.DATE
              }))
              .filter((item: { title: string }) => item.title);
            setNewsData(newsLines);
          }
        }
      } catch (err) {
        console.error("Weekly report fetch failed:", err);
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWeeklyReport();
  }, []);

  // 일간 적금 데이터를 차트 데이터로 변환
  const getBarChartData = () => {
    if (!weeklyData) return {
      labels: ["월", "화", "수", "목", "금", "토", "일"],
      datasets: [{ data: [0, 0, 0, 0, 0, 0, 0] }]
    };

    const sortedDates = Object.keys(weeklyData.DAILY_SAVINGS).sort();
    const data = sortedDates.map(date => weeklyData.DAILY_SAVINGS[date]);

    return {
      labels: ["월", "화", "수", "목", "금", "토", "일"],
      datasets: [{ data }]
    };
  };

  // 승패 기록 포맷팅
  const getTeamRecord = () => {
    if (!weeklyData) return "0승 0패";
    const { WIN, LOSE, DRAW } = weeklyData.TEAM_RECORD;
    return `${WIN}승 ${LOSE}패${DRAW > 0 ? ` ${DRAW}무` : ''}`;
  };

  // --- 가짜 데이터 (기존과 동일) ---
  const weekSummary = {
    period: "3.1 - 3.7",
    totalAmount: "50,000원",
    games: "4승 2패",
  };
  const barData = {
    labels: ["월", "화", "수", "목", "금", "토", "일"],
    datasets: [{ data: [5000, 15000, 7500, 12000, 10000, 18000, 13000] }],
  };
  const pieData = [
    { name: "승리", population: 35, color: "#1E3A8A" },
    { name: "안타", population: 28, color: "#93C5FD" },
    { name: "홈런", population: 22, color: "#BFDBFE" },
    { name: "3연전 승리", population: 15, color: "#DBEAFE" },
  ];
  const teamStats = {
    record: "4승 2패",
    teamBatting: "0.289",
    teamHomeRuns: "8개",
    rankChange: "+2",
  };
  // -----------------------------

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <HeaderTitle width={width}>리포트</HeaderTitle>
          <View style={{ width: 24 }} />
        </Header>

        <SafeAreaView style={{ flex: 1, paddingBottom: 60 }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ padding: width * 0.04, paddingBottom: 20 }}
          >
            {/* 주간 요약 */}
            <Card width={width}>
              <CardHeader width={width}>
                <CardTitle width={width}>
                  주간 요약 ({weeklyData ? new Date(weeklyData.DATE).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' }) : ""})
                </CardTitle>
              </CardHeader>
              <CardContent width={width}>
                <SummaryItem>
                  <SummaryLabel>주간 적립액</SummaryLabel>
                  <SummaryValue teamColor={teamColor.primary}>
                    {weeklyData ? `${weeklyData.WEEKLY_AMOUNT.toLocaleString()}원` : "0원"}
                  </SummaryValue>
                </SummaryItem>
                <SummaryItem>
                  <SummaryLabel>주간 경기</SummaryLabel>
                  <SummaryValue>
                    {weeklyData ? `${weeklyData.TEAM_RECORD.WIN}승 ${weeklyData.TEAM_RECORD.LOSE}패${weeklyData.TEAM_RECORD.DRAW > 0 ? ` ${weeklyData.TEAM_RECORD.DRAW}무` : ''}` : "0승 0패"}
                  </SummaryValue>
                </SummaryItem>
                <SummaryItem style={{ borderBottomWidth: 0 }}>
                  <SummaryValue style={{ fontSize: 14, color: '#666666' }}>
                    {weeklyData?.LLM_CONTEXT 
                      ? weeklyData.LLM_CONTEXT.replace(/\*(.*?)\*/g, '$1') 
                      : "이번 주 요약 정보가 없습니다."}
                  </SummaryValue>
                </SummaryItem>
              </CardContent>
            </Card>

            {/* 주간 적금 현황 */}
            <Card width={width}>
              <CardHeader width={width}>
                <CardTitle width={width}>주간 적금 현황</CardTitle>
              </CardHeader>
              <CardContent width={width}>
                <ChartContainer>
                  <BarChartFallback
                    data={{
                      labels: ["월", "화", "수", "목", "금", "토", "일"],
                      datasets: [{
                        data: weeklyData ? Object.values(weeklyData.DAILY_SAVINGS) : [0, 0, 0, 0, 0, 0, 0]
                      }]
                    }}
                    width={width}
                    teamColor={teamColor.primary}
                  />
                </ChartContainer>
                <View style={{ alignItems: "flex-end", marginTop: 10 }}>
                  <SummaryValue teamColor={teamColor.primary}>
                    주간 총 적금액: {weeklyData ? `${weeklyData.WEEKLY_AMOUNT.toLocaleString()}원` : "0원"}
                  </SummaryValue>
                </View>
              </CardContent>
            </Card>

            {/* === 주석 처리 시작 === */}
            {/*
              {/* 적금 유형별 분석 (파이 차트) *}
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>적금 유형별 분석</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                  <ChartContainer>
                    <CustomDonutChart data={pieData} width={width} />
                  </ChartContainer>
                </CardContent>
              </Card>

              {/* 팀 성적 요약 *}
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>팀 성적 요약</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                  <TeamStatItem>
                    <TeamStatLabel>주간 성적</TeamStatLabel>
                    <TeamStatValue>{teamStats.record}</TeamStatValue>
                  </TeamStatItem>
                  <TeamStatItem>
                    <TeamStatLabel>팀 타율</TeamStatLabel>
                    <TeamStatValue>{teamStats.teamBatting}</TeamStatValue>
                  </TeamStatItem>
                  <TeamStatItem>
                    <TeamStatLabel>팀 홈런</TeamStatLabel>
                    <TeamStatValue>{teamStats.teamHomeRuns}</TeamStatValue>
                  </TeamStatItem>
                  <TeamStatItem style={{ borderBottomWidth: 0 }}>
                    <TeamStatLabel>순위 변동</TeamStatLabel>
                    <TeamStatValue highlight> {teamStats.rankChange} </TeamStatValue>
                  </TeamStatItem>
                </CardContent>
              </Card>
            */}
            {/* === 주석 처리 끝 === */}

            {/* 주간 뉴스 하이라이트 */}
            <Card width={width}>
              <CardHeader width={width}>
                <CardTitle width={width}>주간 뉴스 하이라이트</CardTitle>
              </CardHeader>
              <CardContent width={width}>
                {isLoading ? (
                  <View style={{ padding: 20, alignItems: "center" }}>
                    <Text style={{ fontFamily: theme.fonts.regular }}>
                      뉴스 데이터 로딩 중...
                    </Text>
                  </View>
                ) : error ? (
                  <View style={{ padding: 20, alignItems: "center" }}>
                    <Text style={{ fontFamily: theme.fonts.regular }}>
                      뉴스 데이터 로딩 실패
                    </Text>
                  </View>
                ) : weeklyData?.NEWS_SUMMATION ? (
                  weeklyData.NEWS_SUMMATION.split('\n')
                    .filter(line => line.trim())
                    .map((line, index) => (
                      <NewsItem key={index}>
                        <NewsTitle>{line.trim()}</NewsTitle>
                      </NewsItem>
                    ))
                ) : (
                  <View style={{ padding: 20, alignItems: "center" }}>
                    <Text style={{ fontFamily: theme.fonts.regular }}>
                      이번 주 뉴스 요약이 없습니다.
                    </Text>
                  </View>
                )}
              </CardContent>
            </Card>
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default WeeklyReportScreen;
