// screens/TransactionDetailScreen.tsx
import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  SafeAreaView,
  ScrollView,
  Image,
  FlatList,
  TouchableOpacity,
  Platform,
  useWindowDimensions,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import Icon from "react-native-vector-icons/Ionicons";
import { useTeam } from "@/context/TeamContext";
import { useNavigation, useRoute, CompositeNavigationProp } from "@react-navigation/native";
import { api } from "@/api/axios";
import { getDailySavingDetail } from "@/api/account";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { BottomTabNavigationProp } from "@react-navigation/bottom-tabs";
import { RootStackParamList } from "@/navigation/AppNavigator";

// 스타일드 컴포넌트 인터페이스
interface StyledProps {
  width: number;
}

// API 응답 타입
interface TransactionDetailResponse {
  DATE: string;
  COUNT: number;
  rule_type_name: string;
  record_name: string;
  player_name: string | null;
  unit_amount: number;
  DAILY_SAVING_AMOUNT: number;
  opponent_team_name?: string;  // 상대팀 정보 추가
}

// 화면에 표시할 데이터 타입
interface TransactionDetail extends TransactionDetailResponse {
  records: {
    name: string;
    count: number;
    amount: number;
  }[];
}

// 기본 컴포넌트 스타일
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

const BackButton = styled.TouchableOpacity`
  padding: 8px;
`;

const HeaderTitle = styled.Text<StyledProps>`
  color: white;
  font-size: ${({ width }) => width * 0.046}px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
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

const TransactionHeader = styled.View`
  padding: 16px;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
  background-color: #f9f9f9;
`;

const SectionHeader = styled.View`
  padding: 16px;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
  background-color: #f9f9f9;
`;

const SectionTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  color: #333;
`;

const AmountText = styled.Text`
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

const RecordList = styled.View`
  padding: 16px;
`;

const RecordItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const RecordName = styled.Text`
  font-size: 16px;
  color: #333333;
`;

const RecordAmount = styled.Text`
  font-size: 16px;
  color: ${({ theme }) => theme.colors.primary};
  font-weight: bold;
`;

const MatchInfo = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 16px;
  gap: 8px;
`;

const TeamLogo = styled.Image`
  width: 24px;
  height: 24px;
`;

const DateText = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-left: 8px;
`;

const TotalAmount = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-bottom: 4px;
`;

const AmountValue = styled.Text<{ color: string }>`
  font-size: 20px;
  font-weight: bold;
  color: ${props => props.color};
  margin-bottom: 12px;
`;

const SuccessMessage = styled.View`
  flex-direction: row;
  align-items: center;
  background-color: #F0F8FF;
  padding: 12px;
  border-radius: 8px;
`;

const SuccessIcon = styled.Text`
  font-size: 16px;
  margin-right: 8px;
`;

const SuccessText = styled.Text`
  font-size: 14px;
  color: #333333;
  flex: 1;
`;

// 네비게이션 타입 정의 수정
type TabParamList = {
  적금내역: { viewMode?: string };
  홈: undefined;
  리포트: undefined;
  혜택: undefined;
};

type TransactionDetailScreenNavigationProp = CompositeNavigationProp<
  NativeStackNavigationProp<RootStackParamList, "TransactionDetail">,
  BottomTabNavigationProp<TabParamList>
>;

const TransactionDetailScreen = () => {
  const { teamColor, teamName } = useTeam();
  const navigation = useNavigation<TransactionDetailScreenNavigationProp>();
  const route = useRoute();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 상세 내역 데이터 상태
  const [isLoading, setIsLoading] = useState(true);
  const [transactionDetail, setTransactionDetail] =
    useState<TransactionDetail | null>(null);

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
  const getTeamLogo = (teamName: string | undefined) => {
    if (!teamName) return teamLogos.NC;

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

    return logoMap[teamName] || teamLogos.NC;
  };

  // 데이터 로딩
  useEffect(() => {
    const fetchTransactionDetail = async () => {
      try {
        setIsLoading(true);
        const params = route.params as { id: string };
        if (!params?.id) {
          console.error("ID가 없습니다.");
          return;
        }

        // 경기 결과 API 호출하여 상대팀 정보 가져오기
        const gameResultResponse = await api.get('/api/game/user-team-results', {
          params: { end_date: params.id }
        });
        
        const gameResult = gameResultResponse.data.find(
          (result: any) => result.game_date === params.id
        );

        // API 호출
        const details: TransactionDetailResponse[] = await getDailySavingDetail(params.id);
        console.log("API 응답:", details);
        if (details && details.length > 0) {
          // 첫 번째 항목의 날짜와 vs_team 정보 사용
          const firstDetail = details[0];
          const totalAmount = details.reduce((sum: number, detail: TransactionDetailResponse) => sum + detail.DAILY_SAVING_AMOUNT, 0);
          
          // 전체 데이터를 첫 번째 항목에 포함시켜 저장
          setTransactionDetail({
            ...firstDetail,
            DAILY_SAVING_AMOUNT: totalAmount,
            opponent_team_name: gameResult?.opponent_team_name,  // 상대팀 정보 추가
            records: details.map((detail: TransactionDetailResponse) => ({
              name: detail.record_name,
              count: detail.COUNT,
              amount: detail.DAILY_SAVING_AMOUNT
            }))
          });
        } else {
          console.log("데이터가 없습니다.");
        }
      } catch (error) {
        console.error("상세 내역을 불러오는데 실패했습니다", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransactionDetail();
  }, [route.params]);

  // 뒤로 가기 핸들러
  const handleGoBack = () => {
    navigation.navigate("적금내역", { viewMode: "list" });
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <BackButton onPress={handleGoBack}>
            <Icon name="chevron-back" size={24} color="white" />
          </BackButton>
          <HeaderTitle width={width}>적금 내역</HeaderTitle>
          <View style={{ width: 24 }} />
        </Header>

        <SafeAreaView style={{ flex: 1 }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{
              padding: width * 0.04,
              paddingBottom: 20,
            }}
          >
            {isLoading ? (
              <View style={{ padding: 20, alignItems: "center" }}>
                <Text>상세 내역을 불러오는 중...</Text>
              </View>
            ) : transactionDetail ? (
              <Card width={width}>
                <TransactionHeader>
                  <MatchInfo>
                    <Text style={{ fontSize: 14, color: '#333333', fontWeight: 'bold' }}>vs</Text>
                    <TeamLogo source={getTeamLogo(transactionDetail.opponent_team_name)} />
                    <DateText>{transactionDetail.DATE} 경기</DateText>
                  </MatchInfo>

                  <TotalAmount>총 적립액</TotalAmount>
                  <AmountValue color={teamColor.primary}>
                    +{transactionDetail.DAILY_SAVING_AMOUNT.toLocaleString()}원
                  </AmountValue>
                </TransactionHeader>

                <RecordList>
                  {transactionDetail.records?.map((record, index) => (
                    <RecordItem key={index}>
                      <RecordName>
                        {record.name} {record.count > 1 ? `${record.count}개` : ''}
                      </RecordName>
                      <RecordAmount>+{record.amount.toLocaleString()}원</RecordAmount>
                    </RecordItem>
                  ))}
                </RecordList>
              </Card>
            ) : (
              <View style={{ padding: 20, alignItems: "center" }}>
                <Text>상세 내역을 찾을 수 없습니다.</Text>
              </View>
            )}
          </ScrollView>
        </SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default TransactionDetailScreen;
