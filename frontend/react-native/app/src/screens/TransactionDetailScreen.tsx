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
import MaterialIcons from "react-native-vector-icons/MaterialIcons";

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
  TEXT?: string;  // 설명 텍스트 추가
  SAVING_RULE_TYPE_ID?: number; // 규칙 타입 ID
}

// 화면에 표시할 데이터 타입
interface TransactionDetail extends TransactionDetailResponse {
  records: {
    name: string;
    count: number;
    amount: number;
    ruleType?: string; // 규칙 타입 추가
  }[];
  // 규칙 타입별로 그룹화된 데이터
  recordsByType: {
    [key: string]: {
      typeName: string;
      records: {
        name: string;
        count: number;
        amount: number;
      }[];
      totalAmount: number;
    }
  };
}

// 기본 컴포넌트 스타일
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

const AppWrapper = styled.View`
  flex: 1;
  align-items: center;
  background-color: white;
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

const BackButton = styled.TouchableOpacity`
  padding: 8px;
  z-index: 1;
`;

const Header = styled.View<StyledProps & { teamColor: string }>`
  display: flex;
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
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const AmountText = styled.Text`
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const RecordList = styled.View`
  padding: 0;
`;

const RecordItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
`;

const RecordName = styled.Text`
  font-size: 16px;
  color: #333333;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RecordAmount = styled.Text`
  font-size: 16px;
  color: ${({ theme }) => theme.colors.primary};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const MatchInfo = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  margin-bottom: 16px;
  padding: 4px ${({ width }) => width * 0.01}px;
`;

const TeamLogo = styled.Image<StyledProps>`
  width: ${({ width }) => width * 0.07}px;
  height: ${({ width }) => width * 0.07}px;
  margin-horizontal: ${({ width }) => width * 0.015}px;
  resize-mode: contain;
`;

const DateText = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-left: 8px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const TotalAmount = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-bottom: 4px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const AmountValue = styled.Text<{ color: string }>`
  font-size: 20px;
  font-weight: bold;
  color: ${props => props.color};
  margin-bottom: 12px;
  font-family: ${({ theme }) => theme.fonts.bold};
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
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const DescriptionContainer = styled.View`
  padding: 16px;
  border-top-width: 1px;
  border-top-color: #f0f0f0;
`;

const DescriptionText = styled.Text`
  font-size: 14px;
  color: #666666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RuleTypeHeader = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background-color: #f8f8f8;
  border-top-width: 1px;
  border-top-color: #eeeeee;
`;

const RuleTypeName = styled.Text`
  font-size: 15px;
  font-weight: bold;
  color: #333;
  margin-bottom: 2px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const RuleTypeAmount = styled.Text`
  font-size: 14px;
  color: #1588CF;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
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

        // 거래 내역 조회해서 TEXT 필드 가져오기
        const transferResponse = await api.get('/api/account/transfers_log');
        const transfer = transferResponse.data.find((item: any) => item.DATE === params.id);
        const description = transfer?.TEXT || "";

        // API 호출
        const details: TransactionDetailResponse[] = await getDailySavingDetail(params.id);
        console.log("API 응답:", details);
        if (details && details.length > 0) {
          // 첫 번째 항목의 날짜와 vs_team 정보 사용
          const firstDetail = details[0];
          const totalAmount = details.reduce((sum: number, detail: TransactionDetailResponse) => sum + detail.DAILY_SAVING_AMOUNT, 0);
          
          // 규칙 타입별로 그룹화
          const recordsByType: Record<string, {
            typeName: string;
            records: Array<{
              name: string;
              count: number;
              amount: number;
            }>;
            totalAmount: number;
          }> = {};
          
          // 규칙 타입 매핑 (rule_type_name 필드를 기반으로 그룹화)
          const ruleTypeMapping: Record<string, string> = {
            "홈런": "기본 규칙",
            "안타": "기본 규칙",
            "승리": "기본 규칙", 
            "득점": "기본 규칙",
            "병살타": "상대팀",
            "실책": "상대팀",
            "삼진": "투수",
            "볼넷": "투수",
            "자책": "투수",
            "도루": "타자"
          };
          
          details.forEach(detail => {
            // 규칙 타입 결정 (기본값 설정)
            const typeName = ruleTypeMapping[detail.record_name] || "기본 규칙";
            
            // 해당 타입이 없으면 새로 생성
            if (!recordsByType[typeName]) {
              recordsByType[typeName] = {
                typeName,
                records: [],
                totalAmount: 0
              };
            }
            
            // 해당 타입에 레코드 추가
            recordsByType[typeName].records.push({
              name: detail.record_name,
              count: detail.COUNT,
              amount: detail.DAILY_SAVING_AMOUNT
            });
            
            // 해당 타입의 총액 증가
            recordsByType[typeName].totalAmount += detail.DAILY_SAVING_AMOUNT;
          });
          
          // 전체 데이터를 첫 번째 항목에 포함시켜 저장
          setTransactionDetail({
            ...firstDetail,
            DAILY_SAVING_AMOUNT: totalAmount,
            opponent_team_name: gameResult?.opponent_team_name,  // 상대팀 정보 추가
            TEXT: description,  // 설명 텍스트 추가
            records: details.map((detail: TransactionDetailResponse) => ({
              name: detail.record_name,
              count: detail.COUNT,
              amount: detail.DAILY_SAVING_AMOUNT,
              ruleType: ruleTypeMapping[detail.record_name] || "기본 규칙"
            })),
            recordsByType
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

  // 규칙 타입 순서 정의
  const ruleTypeOrder = {
    "기본 규칙": 1,
    "투수": 2,
    "타자": 3,
    "상대팀": 4
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <BackButton onPress={handleGoBack}>
            <MaterialIcons name="chevron-left" size={28} color="white" />
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
                  <MatchInfo width={width}>
                    <Text style={{ fontSize: 14, color: '#333333', fontWeight: 'bold' }}>vs</Text>
                    <TeamLogo width={width} source={getTeamLogo(transactionDetail.opponent_team_name)} />
                    <DateText>{transactionDetail.DATE} 경기</DateText>
                  </MatchInfo>

                  <TotalAmount>총 적립액</TotalAmount>
                  <AmountValue color={teamColor.primary}>
                    +{transactionDetail.DAILY_SAVING_AMOUNT.toLocaleString()}원
                  </AmountValue>
                  
                  {transactionDetail.TEXT && (
                    <View style={{ marginTop: 8 }}>
                      <Text style={{ fontSize: 14, color: '#666' }}>{transactionDetail.TEXT}</Text>
                    </View>
                  )}
                </TransactionHeader>

                <RecordList>
                  {Object.keys(transactionDetail.recordsByType || {})
                    .sort((a, b) => {
                      return (ruleTypeOrder[a as keyof typeof ruleTypeOrder] || 99) - 
                             (ruleTypeOrder[b as keyof typeof ruleTypeOrder] || 99);
                    })
                    .map((typeKey) => {
                      const typeData = transactionDetail.recordsByType[typeKey];
                      
                      return (
                        <View key={typeKey}>
                          <RuleTypeHeader>
                            <RuleTypeName>{typeData.typeName}</RuleTypeName>
                            <RuleTypeAmount>총 {typeData.totalAmount.toLocaleString()}원</RuleTypeAmount>
                          </RuleTypeHeader>
                          
                          {typeData.records.map((record, index) => (
                            <RecordItem key={`${typeKey}-${index}`}>
                              <RecordName>
                                {record.name} {record.count > 1 ? `${record.count}개` : ''}
                              </RecordName>
                              <RecordAmount>+{record.amount.toLocaleString()}원</RecordAmount>
                            </RecordItem>
                          ))}
                        </View>
                      );
                    })
                  }
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
