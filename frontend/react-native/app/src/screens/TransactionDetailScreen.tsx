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
import { Ionicons } from "@expo/vector-icons";
import { useTeam } from "@/context/TeamContext";
import { useNavigation, useRoute } from "@react-navigation/native";
import { api } from "@/api/axios";
import { getDailySavingDetail } from "@/api/account";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "@/navigation/AppNavigator";

// 스타일드 컴포넌트 인터페이스
interface StyledProps {
  width: number;
}

// 상세 내역 항목 인터페이스
interface TransactionDetail {
  DATE: string;
  COUNT: number;
  rule_type_name: string;
  record_name: string;
  player_name: string | null;
  unit_amount: number;
  DAILY_SAVING_AMOUNT: number;
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

type TransactionDetailScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, "TransactionDetail">;

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
    TWINS: require("../../assets/icon.png"),
    BEARS: require("../../assets/icon.png"),
  };

  // 팀명으로 팀 로고 가져오기
  const getTeamLogo = (teamName: string) => {
    const logoMap: { [key: string]: any } = {
      "LG 트윈스": teamLogos.TWINS,
      "두산 베어스": teamLogos.BEARS,
      TWINS: teamLogos.TWINS,
      BEARS: teamLogos.BEARS,
    };
    return logoMap[teamName] || teamLogos.TWINS;
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

        // API 호출
        const details = await getDailySavingDetail(params.id);
        console.log("API 응답:", details);
        console.log("API 응답 상세:", JSON.stringify(details, null, 2));
        if (details && details.length > 0) {
          setTransactionDetail(details[0]); // 첫 번째 항목 사용
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
    navigation.navigate("Main", {
      screen: "적금내역",
      params: { viewMode: "list" },
    });
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header width={width} teamColor={teamColor.primary}>
          <BackButton onPress={handleGoBack}>
            <Ionicons name="arrow-back" size={24} color="white" />
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
                  <Text style={{ fontSize: 18, fontWeight: "bold", marginBottom: 12 }}>
                    상세 내역
                  </Text>

                  <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 10 }}>
                    <Text style={{ fontWeight: "bold", marginRight: 5 }}>
                      {transactionDetail.record_name}
                    </Text>
                    {transactionDetail.player_name && (
                      <Text style={{ fontSize: 16, fontWeight: "bold" }}>
                        {transactionDetail.player_name}
                      </Text>
                    )}
                  </View>

                  <Text style={{ fontSize: 14, color: "#333", marginBottom: 4 }}>
                    총 적립액:{" "}
                    <Text style={{ fontWeight: "bold", color: teamColor.primary }}>
                      {transactionDetail.DAILY_SAVING_AMOUNT.toLocaleString()}원
                    </Text>
                  </Text>

                  <Text style={{ fontSize: 14, color: "#666" }}>
                    {transactionDetail.rule_type_name}
                  </Text>
                </TransactionHeader>

                <SectionHeader>
                  <SectionTitle>적립 내역</SectionTitle>
                </SectionHeader>

                <View style={{ padding: 16 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", padding: 16, borderBottomWidth: 1, borderBottomColor: "#f0f0f0" }}>
                    <Text style={{ fontSize: 16 }}>단위 금액</Text>
                    <AmountText style={{ fontSize: 16 }}>
                      {transactionDetail.unit_amount.toLocaleString()}원
                    </AmountText>
                  </View>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", padding: 16, borderBottomWidth: 1, borderBottomColor: "#f0f0f0" }}>
                    <Text style={{ fontSize: 16 }}>적립 횟수</Text>
                    <AmountText style={{ fontSize: 16 }}>
                      {transactionDetail.COUNT}회
                    </AmountText>
                  </View>
                </View>
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
