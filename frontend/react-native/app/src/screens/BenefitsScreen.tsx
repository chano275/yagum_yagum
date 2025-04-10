import React, { useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  useWindowDimensions,
  Alert,
  Modal,
  ActivityIndicator,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import { Ionicons } from "@expo/vector-icons";
import { useTeam } from "@/context/TeamContext";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "@/navigation/AppNavigator";
import { api } from "@/api/axios"; // API 클라이언트 임포트

// 네비게이션 타입 정의
type BenefitsScreenNavigationProp =
  NativeStackNavigationProp<RootStackParamList>;

// 예측 결과 인터페이스
interface Prediction {
  PREDICTION_ID: number;
  ACCOUNT_ID: number;
  TEAM_ID: number;
  PREDICTED_RANK: number;
  SEASON_YEAR: number;
  IS_CORRECT: number;
  team_name: string;
}

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

// 팀 컬러를 적용하도록 Header 컴포넌트 수정
const Header = styled.View<{ teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  padding: 20px;
  padding-top: 60px;
  padding-bottom: 15px;
`;

const HeaderTitle = styled.Text`
  color: white;
  font-size: 18px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BenefitCard = styled.View<StyledProps>`
  flex-direction: row;
  align-items: center;
  background-color: white;
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 20px;
  border: 1px solid #f0f0f0;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.05);
  `}
`;

// 수정된 IconContainer 컴포넌트
const IconContainer = styled.View<{ bgColor: string }>`
  width: 40px;
  height: 40px;
  border-radius: 20px;
  background-color: ${(props) =>
    props.bgColor === "#ffffff" ? "#f0f0f0" : props.bgColor};
  border: ${(props) =>
    props.bgColor === "#ffffff" ? "1px solid #dddddd" : "none"};
  justify-content: center;
  align-items: center;
  margin-right: 15px;
`;

const BenefitContent = styled.View`
  flex: 1;
`;

const BenefitTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BenefitDescription = styled.Text`
  font-size: 14px;
  color: #666;
  line-height: 20px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const NavigationArrow = styled.View`
  margin-left: 10px;
`;

// 추가: 로딩 인디케이터 스타일
const LoadingContainer = styled.View`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.7);
  z-index: 10;
`;

// 추가: 모달 관련 스타일 컴포넌트
const ModalOverlay = styled.View`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;

  ${Platform.OS === "web" &&
  `
    position: absolute;
    width: 100%;
    height: 100%;
    align-self: center;
    background-color: rgba(0, 0, 0, 0.5);
    left: 0;
    top: 0;
  `}
`;

const ModalContainer = styled.View`
  width: 80%;
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  align-items: center;
  elevation: 5;
  shadow-opacity: 0.3;
  shadow-radius: 4px;
  shadow-color: #000;
  shadow-offset: 0px 2px;
  max-width: ${BASE_MOBILE_WIDTH * 0.8}px;
  margin: 0 auto;
`;

const ModalTitle = styled.Text`
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ModalMessage = styled.Text`
  font-size: 16px;
  text-align: center;
  margin-bottom: 20px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ModalButton = styled.TouchableOpacity<{ teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  border-radius: 8px;
  padding: 12px 25px;
  align-items: center;
`;

const ModalButtonText = styled.Text`
  color: white;
  font-size: 16px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BenefitsScreen = () => {
  // useTeam 훅을 사용해 팀 컬러 정보 가져오기
  const { teamColor, teamName } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  // 네비게이션 추가
  const navigation = useNavigation<BenefitsScreenNavigationProp>();

  // 모달 및 예측 상태 추가
  const [modalVisible, setModalVisible] = useState(false);
  const [existingPrediction, setExistingPrediction] =
    useState<Prediction | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 기존 예측 확인 함수
  const checkExistingPrediction = async () => {
    try {
      setIsLoading(true);
      const response = await api.get("/api/mission/rank-predictions/check");

      if (response.data && response.data.length > 0) {
        // 사용자가 이미 예측한 경우
        setExistingPrediction(response.data[0]);
        setModalVisible(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Failed to check existing prediction:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // 혜택 데이터
  const benefits = [
    {
      id: "2",
      title: "경기 직관 인증",
      description:
        "홈경기 직관 티켓 인증을 3번 완료하면 우대금리 0.1%p가 추가 제공됩니다.",
      icon: "ticket-outline",
      bgColor: "#FF5252",
      onPress: () => {
        // 티켓 인증 페이지로 이동
        navigation.navigate("Verifyticket", {
          benefitType: "ticket",
          title: "경기 직관 인증",
        });
      },
    },
    {
      id: "4",
      title: "팀 순위 맞추기",
      description:
        "시즌 종료 후 예측한 순위와 실제 순위가 일치하면 우대금리가 제공됩니다.",
      icon: "trophy-outline",
      bgColor: teamColor.secondary,
      onPress: async () => {
        // 사용자가 이미 예측했는지 확인
        const hasPrediction = await checkExistingPrediction();

        if (!hasPrediction) {
          // 기존 예측이 없으면 예측 화면으로 이동
          navigation.navigate("Matchrank", {
            benefitType: "ranking",
            title: "팀 순위 맞추기",
          });
        }
        // 기존 예측이 있으면 checkExistingPrediction에서 모달을 표시
      },
    },
  ];

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        {/* 헤더에 팀 컬러 적용 */}
        <Header teamColor={teamColor.primary}>
          <HeaderTitle>혜택</HeaderTitle>
        </Header>

        <SafeAreaView style={{ flex: 1, backgroundColor: "#F5F5F5" }}>
          <ScrollView
            style={{ flex: 1 }}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ padding: 16 }}
          >
            {benefits.map((benefit) => (
              <TouchableOpacity
                key={benefit.id}
                onPress={benefit.onPress}
                activeOpacity={0.7}
              >
                <BenefitCard width={width}>
                  <IconContainer bgColor={benefit.bgColor}>
                    <Ionicons name={benefit.icon} size={24} color="white" />
                  </IconContainer>
                  <BenefitContent>
                    <BenefitTitle>{benefit.title}</BenefitTitle>
                    <BenefitDescription>
                      {benefit.description}
                    </BenefitDescription>
                  </BenefitContent>
                  <NavigationArrow>
                    <Ionicons
                      name="chevron-forward"
                      size={20}
                      color="#CCCCCC"
                    />
                  </NavigationArrow>
                </BenefitCard>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </SafeAreaView>

        {/* 로딩 인디케이터 */}
        {isLoading && (
          <LoadingContainer>
            <ActivityIndicator size="large" color={teamColor.primary} />
          </LoadingContainer>
        )}

        {/* 기존 예측 정보 모달 */}
        <Modal
          animationType="fade"
          transparent={true}
          visible={modalVisible}
          onRequestClose={() => setModalVisible(false)}
          statusBarTranslucent={true}
          {...(Platform.OS === "web"
            ? {
                supportedOrientations: ["portrait"],
                hardwareAccelerated: true,
              }
            : {})}
        >
          <ModalOverlay>
            <ModalContainer>
              <ModalTitle>순위 예측 내역</ModalTitle>
              <ModalMessage>
                {existingPrediction ? (
                  <>
                    {existingPrediction.team_name}의 예상 순위를{" "}
                    {existingPrediction.PREDICTED_RANK}위로
                    {"\n"}
                    예측하셨습니다.
                    {"\n\n"}
                    우대금리 혜택은 2025 KBO 리그{"\n"}
                    종료 후 적용됩니다.
                  </>
                ) : (
                  "예측 정보를 불러올 수 없습니다."
                )}
              </ModalMessage>

              <ModalButton
                teamColor={teamColor.primary}
                onPress={() => setModalVisible(false)}
              >
                <ModalButtonText>확인</ModalButtonText>
              </ModalButton>
            </ModalContainer>
          </ModalOverlay>
        </Modal>
      </MobileContainer>
    </AppWrapper>
  );
};

export default BenefitsScreen;
