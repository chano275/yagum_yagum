import React, { useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  Platform,
  TouchableOpacity,
  View,
  Text,
  Image,
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
import * as ImagePicker from "expo-image-picker";

// 네비게이션 타입 정의
type TicketVerificationScreenNavigationProp =
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

// 인증 진행 상태 컴포넌트
const ProgressContainer = styled.View`
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
`;

const ProgressTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ProgressBarContainer = styled.View`
  flex-direction: row;
  height: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
`;

const ProgressFill = styled.View<{ width: string; teamColor: string }>`
  width: ${(props) => props.width};
  background-color: ${(props) => props.teamColor};
  border-radius: 5px;
`;

const ProgressText = styled.Text`
  font-size: 14px;
  color: #666;
  text-align: right;
`;

// 사진 업로드 컴포넌트
const UploadCard = styled.View`
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
`;

const UploadTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const UploadArea = styled.TouchableOpacity<{ teamColor: string }>`
  height: 200px;
  border: 2px dashed ${(props) => props.teamColor};
  border-radius: 12px;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
`;

const UploadPlaceholderText = styled.Text`
  font-size: 14px;
  color: #666;
  margin-top: 10px;
  text-align: center;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const SelectedImage = styled.Image`
  width: 100%;
  height: 200px;
  border-radius: 12px;
`;

// 이전 인증 내역 컴포넌트
const HistoryCard = styled.View`
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
`;

const HistoryTitle = styled.Text`
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const HistoryItem = styled.View`
  flex-direction: row;
  padding: 12px 0;
  border-bottom-width: 1px;
  border-bottom-color: #f0f0f0;
  align-items: center;
`;

const HistoryImage = styled.Image`
  width: 60px;
  height: 40px;
  border-radius: 6px;
  margin-right: 12px;
`;

const HistoryInfo = styled.View`
  flex: 1;
`;

const HistoryTeam = styled.Text`
  font-size: 14px;
  font-weight: bold;
  color: #333;
  font-family: ${({ theme }) => theme.fonts.medium};
`;

const HistoryDate = styled.Text`
  font-size: 12px;
  color: #666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const HistoryStatus = styled.Text<{ teamColor: string }>`
  font-size: 12px;
  color: ${(props) => props.teamColor};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

// 버튼 컴포넌트
const SubmitButton = styled.TouchableOpacity<{
  teamColor: string;
  disabled?: boolean;
}>`
  background-color: ${(props) =>
    props.disabled ? "#CCCCCC" : props.teamColor};
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

// 모달 컴포넌트
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

const TicketVerificationScreen = () => {
  const { teamColor, teamName } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);
  const navigation = useNavigation<TicketVerificationScreenNavigationProp>();

  // 상태 변수
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [verificationCount, setVerificationCount] = useState(1); // 현재까지 인증된 횟수
  const [modalVisible, setModalVisible] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // 티켓 검증 상태 추가
  const [verificationStatus, setVerificationStatus] = useState<
    "idle" | "checking" | "success" | "failed"
  >("idle");
  const [failedReason, setFailedReason] = useState<string | null>(null);

  // 인증 내역 데이터
  const verificationHistory = [
    {
      id: 1,
      team: "NC 다이노스 vs 두산 베어스",
      date: "2025-03-15",
      image: require("../../../assets/icon.png"),
      status: "인증 완료",
    },
  ];

  // 사진 선택 핸들러
  const handleSelectImage = async () => {
    try {
      // 카메라 권한 요청 (모바일에서만 필요)
      if (Platform.OS !== "web") {
        const { status } = await ImagePicker.requestCameraPermissionsAsync();
        if (status !== "granted") {
          alert("카메라 접근 권한이 필요합니다.");
          return;
        }
      }

      // 이미지 선택기 실행
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled) {
        // 결과 처리 - 웹과 모바일 모두 호환되도록
        const selectedAsset = result.assets[0];
        console.log("선택된 이미지:", selectedAsset);
        setSelectedImage(selectedAsset.uri);
        // 상태 초기화
        setVerificationStatus("idle");
        setFailedReason(null);
      }
    } catch (error) {
      console.error("이미지 선택 오류:", error);
      alert("이미지를 선택하는 중에 오류가 발생했습니다.");
    }
  };

  // 인증 요청 핸들러
  const handleVerify = () => {
    if (!selectedImage) return;

    setIsProcessing(true);
    setVerificationStatus("checking");

    // 백엔드 OCR 연동 시 대체될 코드
    setTimeout(() => {
      // 랜덤하게 성공/실패 시나리오 테스트 (실제 구현에서는 제거)
      const isSuccess = Math.random() > 0.3;

      if (isSuccess) {
        setVerificationStatus("success");
        setVerificationCount((prev) => prev + 1);
      } else {
        setVerificationStatus("failed");
        setFailedReason(
          "티켓 정보를 읽을 수 없습니다. 더 선명한 이미지로 다시 시도해주세요."
        );
      }

      setModalVisible(true);
      setIsProcessing(false);
    }, 1500);
  };

  // 모달 확인 버튼 핸들러
  const handleConfirm = () => {
    setModalVisible(false);

    // 성공한 경우에만 혜택 페이지로 이동
    if (verificationStatus === "success") {
      try {
        navigation.navigate("Main", { screen: "혜택" });
      } catch (error) {
        console.error("Navigation error:", error);
        navigation.goBack();
      }
    }

    // 실패한 경우 현재 페이지에 머무름
  };

  // 진행률 계산
  const progressPercentage = `${(verificationCount / 3) * 100}%`;

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />

        {/* 헤더 영역 */}
        <Header teamColor={teamColor.primary}>
          <BackButton onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </BackButton>
          <HeaderTitle>경기 직관 인증</HeaderTitle>
        </Header>

        <ContentContainer>
          <ScrollView showsVerticalScrollIndicator={false}>
            {/* 타이틀 및 설명 */}
            <SectionTitle>티켓 인증으로 우대금리 받기</SectionTitle>
            <SectionSubtitle>
              홈경기 티켓 사진을 업로드하여 인증하고 우대금리 혜택을 받으세요.
            </SectionSubtitle>

            {/* 인증 진행 상태 */}
            <ProgressContainer>
              <ProgressTitle>인증 진행 상태</ProgressTitle>
              <ProgressBarContainer>
                <ProgressFill
                  width={progressPercentage}
                  teamColor={teamColor.primary}
                />
              </ProgressBarContainer>
              <ProgressText>{verificationCount}/3회 인증 완료</ProgressText>
            </ProgressContainer>

            {/* 안내 카드 */}
            <InfoCard>
              <InfoTitle>혜택 안내</InfoTitle>
              <InfoContent>
                • 우대금리 혜택{"\n"}- 3회 인증 완료 시:{" "}
                <HighlightText teamColor={teamColor.primary}>
                  0.1%p 추가 우대금리
                </HighlightText>
                {"\n\n"}• 인증 가능 티켓:{"\n"}- {teamName || "NC 다이노스"}{" "}
                홈경기 티켓{"\n"}- 경기 일자, 팀명, 좌석번호가 표시된 실물 티켓
                {"\n"}- 전자티켓 캡처 화면
                {"\n\n"}• 인증 기간: 2025 KBO 정규시즌 기간
              </InfoContent>
            </InfoCard>

            {/* 사진 업로드 영역 */}
            <UploadCard>
              <UploadTitle>티켓 사진 업로드</UploadTitle>

              {selectedImage ? (
                // 선택된 이미지 표시
                <SelectedImage
                  source={{ uri: selectedImage }}
                  resizeMode="cover"
                />
              ) : (
                // 이미지 업로드 영역
                <UploadArea
                  teamColor={teamColor.primary}
                  onPress={handleSelectImage}
                >
                  <Ionicons name="camera" size={40} color={teamColor.primary} />
                  <UploadPlaceholderText>
                    티켓 사진을 선택해주세요.{"\n"}
                    경기 정보와 좌석 번호가 명확히 보이도록 촬영해주세요.
                  </UploadPlaceholderText>
                </UploadArea>
              )}

              {/* 사진 선택 버튼 */}
              <SubmitButton
                teamColor={teamColor.primary}
                onPress={handleSelectImage}
                style={{ marginTop: 10, marginBottom: 0 }}
              >
                <SubmitButtonText>티켓 사진 선택하기</SubmitButtonText>
              </SubmitButton>

              {/* 이미지 선택 후 티켓 인증 과정 안내 */}
              {selectedImage && verificationStatus === "idle" && (
                <InfoContent style={{ marginTop: 10, textAlign: "center" }}>
                  티켓의 경기 정보와 좌석 번호가 명확히 보이는지 확인 후{"\n"}
                  아래 '티켓 인증하기' 버튼을 눌러주세요.
                </InfoContent>
              )}
            </UploadCard>

            {/* 인증 내역 */}
            <HistoryCard>
              <HistoryTitle>인증 내역</HistoryTitle>

              {verificationHistory.map((item) => (
                <HistoryItem key={item.id}>
                  <HistoryImage source={item.image} />
                  <HistoryInfo>
                    <HistoryTeam>{item.team}</HistoryTeam>
                    <HistoryDate>{item.date}</HistoryDate>
                  </HistoryInfo>
                  <HistoryStatus teamColor={teamColor.primary}>
                    {item.status}
                  </HistoryStatus>
                </HistoryItem>
              ))}

              {verificationHistory.length === 0 && (
                <UploadPlaceholderText>
                  인증 내역이 없습니다.
                </UploadPlaceholderText>
              )}
            </HistoryCard>

            {/* 인증 요청 버튼 */}
            <SubmitButton
              teamColor={teamColor.primary}
              disabled={!selectedImage || isProcessing}
              onPress={handleVerify}
            >
              <SubmitButtonText>
                {isProcessing ? "티켓 정보 분석 중..." : "티켓 인증하기"}
              </SubmitButtonText>
            </SubmitButton>
          </ScrollView>
        </ContentContainer>

        {/* 인증 완료/실패 모달 */}
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
              <ModalTitle>
                {verificationStatus === "success"
                  ? "티켓 인증 완료"
                  : "티켓 인증 실패"}
              </ModalTitle>
              <ModalMessage>
                {verificationStatus === "success" ? (
                  <>
                    {teamName || "NC 다이노스"} 경기 티켓 인증이 완료되었습니다.
                    {"\n\n"}
                    현재 {verificationCount}/3회 인증 완료
                    {verificationCount === 3
                      ? "\n\n축하합니다! 0.1%p 우대금리가 적용되었습니다."
                      : `\n\n${
                          3 - verificationCount
                        }회 더 인증하면 우대금리가 적용됩니다.`}
                  </>
                ) : (
                  <>
                    티켓 인증에 실패했습니다.
                    {"\n\n"}
                    {failedReason}
                    {"\n\n"}
                    다른 이미지로 다시 시도해주세요.
                  </>
                )}
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

export default TicketVerificationScreen;
