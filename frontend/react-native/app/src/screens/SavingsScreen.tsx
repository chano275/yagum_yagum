import React, { useState } from "react";
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
import { useTeam } from "@/context/TeamContext";

// 동적 스타일링을 위한 인터페이스
interface StyledProps {
  width: number;
}

// 모바일 기준 너비 설정 (HomeScreen과 동일)
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

const ProgressFill = styled.View`
  height: 100%;
  width: 100%;
  background-color: #2196f3;
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

const MainPage = () => {
  const { teamColor } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        {/* 헤더 부분 - 팀 색상 적용 */}
        <Header width={width} teamColor={teamColor.primary}>
          <HeaderTitle width={width}>적금 내역 페이지</HeaderTitle>
          <TouchableOpacity>
            <BellIcon
              source={require("../../assets/icon.png")}
              tintColor="yellow"
            />
          </TouchableOpacity>
        </Header>

        <SafeAreaView style={{ flex: 1, paddingBottom: 60 }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: 20 }}
          >
            {/* 유니폼 구매 진행 상황 - 팀 색상 적용 */}
            <ProgressSection width={width} teamColor={teamColor.primary}>
              <ProgressTitle width={width}>유니폼 구매</ProgressTitle>
              <ProgressAmount width={width}>
                487,000원 / 300,000원
              </ProgressAmount>
              <ProgressBarContainer width={width}>
                <ProgressFill />
              </ProgressBarContainer>
              <ProgressPercent width={width}>100% 달성</ProgressPercent>
            </ProgressSection>

            {/* 금리 및 팀 순위 정보 */}
            <StatsRow width={width}>
              <StatText width={width}>
                현재 금리: 3.5% <StatHighlight>+0.4%</StatHighlight>
              </StatText>
              <StatText width={width}>
                팀 순위: 3위 <StatHighlight>+2</StatHighlight>
              </StatText>
            </StatsRow>

            <View style={{ padding: width * 0.04 }}>
              {/* 카드 내용들 */}
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>오늘의 적금 비교</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                  <CardText width={width}>
                    <RedText teamColor={teamColor.primary}>↗</RedText> 두산이
                    승리했지만, 우리팀의 적금이 2배 더 많네요!
                  </CardText>
                </CardContent>
              </Card>

              {/* 적금 규칙 */}
              <Card width={width}>
                {/* 카드 내용 유지 */}
                <CardHeader width={width}>
                  <CardTitle width={width}>적금 규칙</CardTitle>
                </CardHeader>
                <CardContent width={width}>
                  <RuleText width={width}>안타 1개당: 1,000원</RuleText>
                  <RuleText width={width}>홈런 1개당: 5,000원</RuleText>
                  <RuleText width={width}>팀 승리 시: 3,000원</RuleText>
                </CardContent>
              </Card>

              {/* 최근 적금 내역 카드 - 링크와 금액에 팀 색상 적용 */}
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>최근 적금 내역</CardTitle>
                  <TouchableOpacity>
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

              {/* 다음 경기 일정 카드 - 링크에 팀 색상 적용 */}
              <Card width={width}>
                <CardHeader width={width}>
                  <CardTitle width={width}>다음 경기 일정</CardTitle>
                  <TouchableOpacity>
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
