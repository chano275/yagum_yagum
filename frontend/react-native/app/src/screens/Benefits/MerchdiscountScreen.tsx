import React, { useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  Text,
  useWindowDimensions,
  Modal,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import styled from "styled-components/native";
import { Ionicons } from "@expo/vector-icons";
import { useTeam } from "@/context/TeamContext";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "@/navigation/AppNavigator";

// 네비게이션 타입 정의
type MatchrankScreenNavigationProp =
  NativeStackNavigationProp<RootStackParamList>;

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
  background-color: #f7f7f7;
  width: 100%;
  overflow: hidden;
  position: relative;
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
`;

const Header = styled.View<{ teamColor: string }>`
  flex-direction: row;
  align-items: center;
  background-color: ${(props) => props.teamColor};
  padding: 20px;
  padding-top: 60px;
  padding-bottom: 15px;
`;

const BackButton = styled.TouchableOpacity`
  margin-right: 15px;
`;

const HeaderTitle = styled.Text`
  color: white;
  font-size: 18px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ContentContainer = styled.View`
  padding: 20px;
  flex: 1;
`;

const SectionTitle = styled.Text`
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const SectionSubtitle = styled.Text`
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const InfoCard = styled.View`
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
  elevation: 2;
  shadow-opacity: 0.1;
  shadow-radius: 4px;
  shadow-color: #000;
  shadow-offset: 0px 2px;
`;

const InfoTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const InfoContent = styled.Text`
  font-size: 14px;
  color: #666;
  line-height: 20px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const HighlightText = styled.Text<{ teamColor: string }>`
  color: ${(props) => props.teamColor};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const TeamCard = styled.View<{ teamColor: string }>`
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
  elevation: 2;
  shadow-opacity: 0.1;
  shadow-radius: 4px;
  shadow-color: #000;
  shadow-offset: 0px 2px;
`;

const TeamInfo = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 20px;
`;

const TeamLogo = styled.Image`
  width: 60px;
  height: 60px;
  margin-right: 15px;
`;

const TeamName = styled.Text`
  font-size: 20px;
  font-weight: bold;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const RankTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const RankButtonsContainer = styled.View`
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 10px;
`;

const RankButton = styled.TouchableOpacity<{
  selected: boolean;
  teamColor: string;
}>`
  width: 18%;
  height: 48px;
  border-radius: 8px;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
  background-color: ${(props) => (props.selected ? props.teamColor : "white")};
  border: 1px solid ${(props) => (props.selected ? props.teamColor : "#ddd")};
`;

const RankButtonText = styled.Text<{ selected: boolean }>`
  font-size: 18px;
  font-weight: bold;
  color: ${(props) => (props.selected ? "white" : "#333")};
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const SubmitButton = styled.TouchableOpacity<{ teamColor: string }>`
  background-color: ${(props) => props.teamColor};
  border-radius: 8px;
  padding: 16px;
  align-items: center;
  margin-top: 20px;
  margin-bottom: 30px;
`;

const SubmitButtonText = styled.Text`
  color: white;
  font-size: 16px;
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

// 모달 관련 스타일 컴포넌트 추가
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

const MatchrankScreen = () => {
  const { teamColor, teamName } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);
  const navigation = useNavigation<MatchrankScreenNavigationProp>();

  // 선택한 순위 상태
  const [selectedRank, setSelectedRank] = useState<number | null>(null);
  // 모달 표시 상태
  const [modalVisible, setModalVisible] = useState(false);

  // 팀 로고 (예시)
  const teamLogo = require("../../../assets/icon.png"); // 실제 구현시 팀에 맞는 로고로 변경

  // 순위 버튼 생성 (1~10)
  const rankButtons = Array.from({ length: 10 }, (_, i) => i + 1);

  // 제출 버튼 클릭 핸들러
  const handleSubmit = () => {
    if (selectedRank !== null) {
      setModalVisible(true);
    }
  };

  // 모달 확인 버튼 핸들러
  const handleConfirm = () => {
    setModalVisible(false);

    // 네비게이션 처리 개선
    try {
      // 메인 탭 네비게이션으로 이동 (중첩 네비게이션 사용)
      navigation.navigate("Main", { screen: "혜택" });
    } catch (error) {
      console.error("Navigation error:", error);
      // 오류 발생 시 뒤로 가기로 대체
      navigation.goBack();
    }
  };

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />

        {/* 헤더 영역 */}
        <Header teamColor={teamColor.primary}>
          <BackButton onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </BackButton>
          <HeaderTitle>팀 굿즈 할인</HeaderTitle>
        </Header>

        <ContentContainer>
          <ScrollView showsVerticalScrollIndicator={false}>
            {/* 타이틀 및 설명 */}
            <SectionTitle>팀 굿즈 할인 페이지</SectionTitle>
            <SectionSubtitle>
              응원하는 팀의 최종 순위를 예측하고 우대금리 혜택을 받으세요.
            </SectionSubtitle>

            {/* 안내 카드 */}
            <InfoCard>
              <InfoTitle>혜택 안내</InfoTitle>
              <InfoContent>
                • 예측 정확도에 따른 우대금리{"\n"}- 정확히 맞춤:{" "}
                <HighlightText teamColor={teamColor.primary}>
                  0.5%p
                </HighlightText>
                {"\n"}- 1단계 차이:{" "}
                <HighlightText teamColor={teamColor.primary}>
                  0.3%p
                </HighlightText>
                {"\n"}- 2단계 차이:{" "}
                <HighlightText teamColor={teamColor.primary}>
                  0.1%p
                </HighlightText>
                {"\n"}
                {"\n"}• 예측 기간: 2025.04.01 ~ 2025.06.30{"\n"}• 결과 반영:
                2025 KBO 리그 정규시즌 종료 후 1주일 이내
              </InfoContent>
            </InfoCard>

            {/* 팀 정보 및 순위 선택 */}
            <TeamCard teamColor={teamColor.primary}>
              <TeamInfo>
                <TeamLogo source={teamLogo} />
                <TeamName>{teamName || "NC 다이노스"}</TeamName>
              </TeamInfo>
              <RankTitle>예상 순위를 선택해주세요</RankTitle>
              <RankButtonsContainer>
                {rankButtons.map((rank) => (
                  <RankButton
                    key={rank}
                    selected={selectedRank === rank}
                    teamColor={teamColor.primary}
                    onPress={() => setSelectedRank(rank)}
                  >
                    <RankButtonText selected={selectedRank === rank}>
                      {rank}위
                    </RankButtonText>
                  </RankButton>
                ))}
              </RankButtonsContainer>
            </TeamCard>

            {/* 제출 버튼 */}
            <SubmitButton
              teamColor={teamColor.primary}
              disabled={selectedRank === null}
              onPress={handleSubmit}
            >
              <SubmitButtonText>예측 순위 제출하기</SubmitButtonText>
            </SubmitButton>
          </ScrollView>
        </ContentContainer>

        {/* 커스텀 모달 */}
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
              <ModalTitle>순위 예측 완료</ModalTitle>
              <ModalMessage>
                {teamName || "NC 다이노스"}의 예상 순위 {selectedRank}위가
                제출되었습니다.
                {"\n\n"}
                우대금리 혜택은 2025 KBO 리그 종료 후 적용됩니다.
              </ModalMessage>
              <ModalButton
                teamColor={teamColor.primary}
                onPress={handleConfirm}
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

export default MatchrankScreen;
