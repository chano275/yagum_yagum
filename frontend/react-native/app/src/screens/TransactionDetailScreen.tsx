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

// 스타일드 컴포넌트 인터페이스
interface StyledProps {
  width: number;
}

// 상세 내역 항목 인터페이스
interface TransactionDetail {
  id: string;
  date: string;
  opponent: string;
  description: string;
  amount: number;
  items: {
    title: string;
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

const TransactionDetailScreen = () => {
  const { teamColor, teamName } = useTeam();
  const navigation = useNavigation();
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
        // 추후 API 호출로 대체될 예정
        // 현재는 더미 데이터 사용
        const id = route.params?.id;

        // 임시 더미 데이터
        const dummyDetail: TransactionDetail = {
          id: id as string,
          date: "3/12",
          opponent: "TWINS",
          description: "최형우의 시원한 홈런포로 팀이 승리를 거머쥐었습니다!",
          amount: 15000,
          items: [
            { title: "승리", amount: 3000 },
            { title: "안타 8개", amount: 8000 },
            { title: "홈런 2개", amount: 4000 },
          ],
        };

        // 실제 API 호출이 필요할 경우:
        // const response = await api.get(`/api/transaction/${id}`);
        // setTransactionDetail(response.data);

        setTransactionDetail(dummyDetail);
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
    // goBack() 대신 navigate를 사용하여 Main 스크린의 Savings 탭으로 이동하면서 viewMode 파라미터 전달
    navigation.navigate("Main", {
      screen: "적금내역", // 또는 'Savings' - 실제 사용 중인 탭 이름으로 변경
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
                  <Text
                    style={{
                      fontSize: 18,
                      fontWeight: "bold",
                      marginBottom: 12,
                    }}
                  >
                    상세 내역
                  </Text>

                  <View
                    style={{
                      flexDirection: "row",
                      alignItems: "center",
                      marginBottom: 10,
                    }}
                  >
                    <Text style={{ fontWeight: "bold", marginRight: 5 }}>
                      vs
                    </Text>
                    <Image
                      source={getTeamLogo(transactionDetail.opponent)}
                      style={{ width: 36, height: 36, marginRight: 10 }}
                    />
                    <Text style={{ fontSize: 16, fontWeight: "bold" }}>
                      {transactionDetail.date} 경기
                    </Text>
                  </View>

                  <Text
                    style={{ fontSize: 14, color: "#333", marginBottom: 4 }}
                  >
                    총 적립액:{" "}
                    <Text
                      style={{ fontWeight: "bold", color: teamColor.primary }}
                    >
                      {transactionDetail.amount.toLocaleString()}원
                    </Text>
                  </Text>

                  <Text style={{ fontSize: 14, color: "#666" }}>
                    {transactionDetail.description}
                  </Text>
                </TransactionHeader>

                <SectionHeader>
                  <SectionTitle>적립 내역</SectionTitle>
                </SectionHeader>

                <FlatList
                  data={transactionDetail.items}
                  keyExtractor={(item, index) => `item-${index}`}
                  renderItem={({ item }) => (
                    <View
                      style={{
                        flexDirection: "row",
                        justifyContent: "space-between",
                        padding: 16,
                        borderBottomWidth: 1,
                        borderBottomColor: "#f0f0f0",
                      }}
                    >
                      <Text style={{ fontSize: 16 }}>{item.title}</Text>
                      <AmountText style={{ fontSize: 16 }}>
                        +{item.amount.toLocaleString()}원
                      </AmountText>
                    </View>
                  )}
                  scrollEnabled={false}
                />
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
