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

const BackButton = styled.TouchableOpacity`
  padding: 8px;
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
`;

const SummaryValue = styled.Text<{ teamColor?: string; positive?: boolean }>`
  font-size: 16px;
  font-weight: bold;
  color: ${(props) =>
    props.positive ? "#4CAF50" : props.teamColor ? props.teamColor : "#333"};
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
`;

const TeamStatValue = styled.Text<{ highlight?: boolean }>`
  font-size: 14px;
  font-weight: ${(props) => (props.highlight ? "bold" : "normal")};
  color: ${(props) => (props.highlight ? "#4CAF50" : "#333")};
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
`;

const NewsDate = styled.Text`
  font-size: 12px;
  color: #999;
`;

// 막대 차트 컴포넌트
const BarChartFallback = ({ data, width, teamColor }) => {
  const maxValue = Math.max(...data.datasets[0].data);

  return (
    <View style={{ width: width * 0.85, height: 220 }}>
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          height: 180,
          alignItems: "flex-end",
        }}
      >
        {data.labels.map((label, index) => {
          const value = data.datasets[0].data[index];
          const barHeight = (value / maxValue) * 160;

          return (
            <View key={index} style={{ alignItems: "center", flex: 1 }}>
              <View
                style={{
                  width: 30,
                  height: barHeight,
                  backgroundColor: teamColor,
                  borderTopLeftRadius: 4,
                  borderTopRightRadius: 4,
                }}
              />
              <Text style={{ marginTop: 5, fontSize: 12, color: "#666" }}>
                {label}
              </Text>
              <Text style={{ fontSize: 10, color: "#999" }}>
                {value.toLocaleString()}원
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
};

// 커스텀 도넛 차트 (SVG 대신 React Native View 사용)
const CustomDonutChart = ({ data, width }) => {
  const totalAmount = 78500;
  const total = data.reduce((sum, item) => sum + item.population, 0);

  return (
    <View style={{ width: width * 0.85, alignItems: "center" }}>
      {/* 차트 상단 정보 */}
      <View style={{ marginBottom: 20, alignItems: "center" }}>
        <Text style={{ fontSize: 16, fontWeight: "bold", color: "#333" }}>
          적금 유형별 분석
        </Text>
      </View>

      {/* 데이터 표시 */}
      <View
        style={{
          width: "100%",
          padding: 10,
          backgroundColor: "#f8f9fa",
          borderRadius: 8,
          marginBottom: 15,
        }}
      >
        {data.map((item, index) => {
          const amount = Math.round((item.population / 100) * totalAmount);

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
                  <Text style={{ fontWeight: "bold", color: "#333" }}>
                    {item.name}
                  </Text>
                </View>
                <Text style={{ fontWeight: "bold", color: "#333" }}>
                  {item.population}%
                </Text>
              </View>

              {/* 프로그레스 바 */}
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
                }}
              >
                {amount.toLocaleString()}원
              </Text>
            </View>
          );
        })}
      </View>

      {/* 총 금액 표시 */}
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
        <Text style={{ fontWeight: "bold", color: "#333" }}>총 적립액</Text>
        <Text style={{ fontWeight: "bold", color: "#1E3A8A" }}>
          {totalAmount.toLocaleString()}원
        </Text>
      </View>
    </View>
  );
};

const WeeklyReportScreen = ({ navigation }) => {
  const { teamColor, teamName, currentTeam } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 뉴스 데이터 상태 추가
  const [newsData, setNewsData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 팀 이름으로 팀 ID 가져오기
  const getTeamIdByName = (name) => {
    const teamMapping = {
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

  // API에서 뉴스 데이터 가져오기
  useEffect(() => {
    const fetchWeeklyReport = async () => {
      try {
        setIsLoading(true);
        // teamName을 기준으로 teamId 결정
        const teamId = getTeamIdByName(teamName);

        const response = await api.get(`/api/report/weekly/team/${teamId}`);

        if (response.status === 200) {
          setNewsData(response.data);
        }
      } catch (err) {
        console.error("Weekly report fetch failed:", err);
        setError(err);
        // 에러 발생 시 빈 데이터 설정
        setNewsData([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWeeklyReport();
  }, [teamName]); // teamName이 변경될 때마다 다시 가져오기

  // API 응답에서 뉴스 데이터 처리
  const processNewsData = () => {
    if (newsData.length === 0 || !newsData[0]?.NEWS_SUMMATION) {
      // API 호출 실패 시 기본 뉴스 데이터 반환
      return [
        {
          id: 1,
          title: "뉴스 데이터가 불러와 지지 않았습니다.",
          date: "2025.01.01",
        },
      ];
    }

    const newsItem = newsData[0];

    // 문자열을 줄바꿈으로 분리하고 뉴스 아이템 생성
    return newsItem.NEWS_SUMMATION.split("\n").map((news, index) => {
      // 앞에 "- "가 있으면 제거
      const title = news.startsWith("- ") ? news.substring(2) : news;

      return {
        id: index + 1,
        title,
        date: newsItem.DATE || "2025.04.03",
      };
    });
  };

  // 가공된 뉴스 데이터 가져오기
  const newsHighlights = processNewsData();

  // 주간 요약 데이터
  const weekSummary = {
    period: "3.1 - 3.7",
    totalAmount: "50,000원",
    games: "4승 2패",
  };

  // 주간 적금 현황 데이터 (막대 그래프)
  const barData = {
    labels: ["월", "화", "수", "목", "금", "토", "일"],
    datasets: [
      {
        data: [5000, 15000, 7500, 12000, 10000, 18000, 13000],
      },
    ],
  };

  // 적금 유형별 분석 데이터 (파이 차트)
  const pieData = [
    {
      name: "승리",
      population: 35,
      color: "#1E3A8A",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12,
    },
    {
      name: "안타",
      population: 28,
      color: "#93C5FD",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12,
    },
    {
      name: "홈런",
      population: 22,
      color: "#BFDBFE",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12,
    },
    {
      name: "3연전 승리",
      population: 15,
      color: "#DBEAFE",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12,
    },
  ];

  // 팀 성적 요약 데이터
  const teamStats = {
    record: "4승 2패",
    teamBatting: "0.289",
    teamHomeRuns: "8개",
    rankChange: "+2",
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <BackButton onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </BackButton>
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
                  주간 요약 ({weekSummary.period})
                </CardTitle>
              </CardHeader>
              <CardContent width={width}>
                <SummaryItem>
                  <SummaryLabel>주간 적립액</SummaryLabel>
                  <SummaryValue teamColor={teamColor.primary}>
                    {weekSummary.totalAmount}
                  </SummaryValue>
                </SummaryItem>
                <SummaryItem>
                  <SummaryLabel>주간 경기</SummaryLabel>
                  <SummaryValue>{weekSummary.games}</SummaryValue>
                </SummaryItem>
                <SummaryItem style={{ borderBottomWidth: 0 }}>
                  <SummaryLabel>이번 주 증가율</SummaryLabel>
                  <SummaryValue positive>+23%</SummaryValue>
                </SummaryItem>
              </CardContent>
            </Card>

            {/* 주간 적금 현황 (막대 그래프) */}
            <Card width={width}>
              <CardHeader width={width}>
                <CardTitle width={width}>주간 적금 현황</CardTitle>
              </CardHeader>
              <CardContent width={width}>
                <ChartContainer>
                  <BarChartFallback
                    data={barData}
                    width={width}
                    teamColor={teamColor.primary}
                  />
                </ChartContainer>
                <View style={{ alignItems: "flex-end", marginTop: 10 }}>
                  <SummaryValue teamColor={teamColor.primary}>
                    주간 총 적금액: 78,500원
                  </SummaryValue>
                </View>
              </CardContent>
            </Card>

            {/* 적금 유형별 분석 (파이 차트) */}
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

            {/* 팀 성적 요약 */}
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
                  <TeamStatValue highlight>
                    {teamStats.rankChange}
                  </TeamStatValue>
                </TeamStatItem>
              </CardContent>
            </Card>

            {/* 주간 뉴스 하이라이트 - 변경된 부분 */}
            <Card width={width}>
              <CardHeader width={width}>
                <CardTitle width={width}>주간 뉴스 하이라이트</CardTitle>
              </CardHeader>
              <CardContent width={width}>
                {isLoading ? (
                  <View style={{ padding: 20, alignItems: "center" }}>
                    <Text>뉴스 데이터 로딩 중...</Text>
                  </View>
                ) : error ? (
                  <View style={{ padding: 20, alignItems: "center" }}>
                    <Text>뉴스 데이터 로딩 실패</Text>
                  </View>
                ) : (
                  newsHighlights.map((news) => (
                    <NewsItem key={news.id}>
                      <NewsTitle>• {news.title}</NewsTitle>
                      <NewsDate>{news.date}</NewsDate>
                    </NewsItem>
                  ))
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
