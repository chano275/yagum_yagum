import React, { useState, useEffect } from "react";
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
import {
  launchImageLibraryAsync,
  requestCameraPermissionsAsync,
  ImagePickerResult,
  ImagePickerAsset,
} from "expo-image-picker";
import { api } from "@/api/axios";
import axios from "axios";
import { useAccountStore } from "@/store/useStore";

// 네비게이션 타입 정의
type TicketVerificationScreenNavigationProp =
  NativeStackNavigationProp<RootStackParamList>;

// 동적 스타일링을 위한 인터페이스
interface StyledProps {
  width: number;
}

// 우대금리 정보 인터페이스 추가
interface InterestDetails {
  base_interest_rate: number;
  mission_interest_rate: number;
  total_interest_rate: number;
  total_mission_rate: number;
  mission_details: {
    mission_id: number;
    mission_name: string;
    mission_rate: number;
    current_count: number;
    max_count: number;
    is_completed: boolean;
  }[];
}

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// --- 스타일 컴포넌트 정의 ---
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
  background-color: ${(props) => props.teamColor || "#007AFF"};
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
  color: ${(props) => props.teamColor || "#007AFF"};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

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
  background-color: ${(props) => props.teamColor || "#007AFF"};
  border-radius: 5px;
`;

const ProgressText = styled.Text`
  font-size: 14px;
  color: #666;
  text-align: right;
`;

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
  border: 2px dashed ${(props) => props.teamColor || "#007AFF"};
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

const SubmitButton = styled.TouchableOpacity<{
  teamColor: string;
  disabled?: boolean;
}>`
  background-color: ${(props) =>
    props.disabled ? "#CCCCCC" : props.teamColor || "#007AFF"};
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
  `position: absolute; width: 100%; height: 100%; align-self: center; background-color: rgba(0, 0, 0, 0.5); left: 0; top: 0;`}
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
  background-color: ${(props) => props.teamColor || "#007AFF"};
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
  const { teamColor = { primary: "#007AFF" }, teamName } = useTeam();
  const { width: windowWidth } = useWindowDimensions();
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);
  const navigation = useNavigation<TicketVerificationScreenNavigationProp>();
  const { fetchAccountInfo } = useAccountStore();

  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedAssetInfo, setSelectedAssetInfo] =
    useState<ImagePickerAsset | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<
    "idle" | "checking" | "success" | "failed"
  >("idle");
  const [failedReason, setFailedReason] = useState<string | null>(null);

  // 우대금리 정보 상태 추가
  const [interestDetails, setInterestDetails] =
    useState<InterestDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 현재 티켓 인증 횟수와 최대 인증 횟수
  const ticketMission = interestDetails?.mission_details.find(
    (mission) => mission.mission_name === "직관 인증시 우대금리"
  );

  const currentCount = ticketMission?.current_count || 0;
  const maxCount = ticketMission?.max_count || 5;
  const missionRate = ticketMission?.mission_rate || 0.1;

  // 우대금리 정보 가져오기
  const fetchInterestDetails = async () => {
    try {
      setIsLoading(true);
      const response = await api.get("/api/account/interest-details");
      setInterestDetails(response.data);
      console.log("우대금리 정보:", response.data);
    } catch (error) {
      console.error("우대금리 정보 가져오기 오류:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // 컴포넌트 마운트 시 우대금리 정보 가져오기
  useEffect(() => {
    fetchInterestDetails();
  }, []);

  const handleSelectImage = async () => {
    try {
      if (Platform.OS !== "web") {
        const { status } = await requestCameraPermissionsAsync();
        if (status !== "granted") {
          alert("카메라 접근 권한이 필요합니다.");
          return;
        }
      }
      const result: ImagePickerResult = await launchImageLibraryAsync({
        mediaTypes: ["images"],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });
      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        console.log("선택된 이미지:", asset);
        setSelectedImage(asset.uri);
        setSelectedAssetInfo(asset);
        setVerificationStatus("idle");
        setFailedReason(null);
      }
    } catch (error) {
      console.error("이미지 선택 오류:", error);
      alert("이미지를 선택하는 중에 오류가 발생했습니다.");
    }
  };

  const handleVerify = async () => {
    if (!selectedImage || !selectedAssetInfo) return;
    setIsProcessing(true);
    setVerificationStatus("checking");
    try {
      const formData = new FormData();
      const assetMimeType = selectedAssetInfo.mimeType || "image/jpeg";
      let fileExt = "jpg";
      if (assetMimeType === "image/png") {
        fileExt = "png";
      } else if (assetMimeType === "image/gif") {
        fileExt = "gif";
      } else if (assetMimeType === "image/bmp") {
        fileExt = "bmp";
      } else if (assetMimeType === "image/jpeg") {
        fileExt = "jpeg";
      }
      const fileName = `ticket_${Date.now()}.${fileExt}`;
      const correctMimeType = assetMimeType;
      console.log(
        `[handleVerify] 생성된 파일명: ${fileName}, MIME 타입: ${correctMimeType}`
      );
      if (Platform.OS === "web") {
        const response = await fetch(selectedImage);
        const blob = await response.blob();
        formData.append("file", blob, fileName);
        // Web 환경에서 FormData 로깅
        console.log("Web FormData 파일 추가됨");
      } else {
        const fileObject = {
          uri: selectedImage,
          name: fileName,
          type: correctMimeType,
        };
        formData.append("file", fileObject as any);
      }
      const response = await api.post("/api/mission/ocr", formData);
      console.log("OCR API 응답:", response.data);

      if (response.data.success) {
        setVerificationStatus("success");
        // 인증 성공 후 우대금리 정보 다시 가져오기
        await fetchInterestDetails();
        // 계좌 정보도 갱신
        await fetchAccountInfo();
      } else {
        setVerificationStatus("failed");
        setFailedReason(
          response.data.error ||
            "티켓 정보를 읽을 수 없습니다. 더 선명한 이미지로 다시 시도해주세요."
        );
      }
    } catch (error: any) {
      console.error("티켓 인증 API 오류:", error);
      let detailedError = "티켓 인증 중 오류가 발생했습니다.";
      if (axios.isAxiosError(error) && error.response) {
        console.error("--- 상세 오류 정보 ---");
        console.error("상태 코드:", error.response.status);
        console.error(
          "응답 데이터:",
          JSON.stringify(error.response.data, null, 2)
        );
        if (
          error.response.data?.detail &&
          Array.isArray(error.response.data.detail) &&
          error.response.data.detail.length > 0
        ) {
          const validationError = error.response.data.detail[0];
          console.error(
            "Validation 상세 내용:",
            JSON.stringify(validationError, null, 2)
          );
          detailedError =
            validationError?.msg ||
            `서버 유효성 검사 실패 (${JSON.stringify(validationError)})`;
        } else if (error.response.data?.error) {
          detailedError = error.response.data.error;
        } else {
          detailedError = `서버 오류 (${error.response.status})`;
        }
        console.error("----------------------");
      } else if (error instanceof Error) {
        detailedError = error.message;
      } else {
        detailedError = "알 수 없는 오류 발생";
      }
      setVerificationStatus("failed");
      setFailedReason(detailedError);
    } finally {
      setModalVisible(true);
      setIsProcessing(false);
    }
  };

  const handleConfirm = () => {
    setModalVisible(false);
    if (verificationStatus === "success") {
      try {
        navigation.navigate("Main", { screen: "혜택" });
      } catch (error) {
        console.error("Navigation error:", error);
        navigation.goBack();
      }
    }
  };

  const progressPercentage = `${Math.min(
    (currentCount / maxCount) * 100,
    100
  )}%`;

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <StatusBar style="light" />
        <Header teamColor={teamColor.primary}>
          <BackButton onPress={() => navigation.goBack()}>
            <Ionicons name="arrow-back" size={24} color="white" />
          </BackButton>
          <HeaderTitle>경기 직관 인증</HeaderTitle>
        </Header>
        <ContentContainer>
          <ScrollView showsVerticalScrollIndicator={false}>
            <SectionTitle>티켓 인증으로 우대금리 받기</SectionTitle>
            <SectionSubtitle>
              경기 티켓 사진을 업로드하여 인증하고 우대금리 혜택을 받으세요.
            </SectionSubtitle>

            <ProgressContainer>
              <ProgressTitle>인증 진행 상태</ProgressTitle>
              <ProgressBarContainer>
                <ProgressFill
                  width={progressPercentage}
                  teamColor={teamColor.primary}
                />
              </ProgressBarContainer>
              <ProgressText>
                {currentCount}/{maxCount}회 인증 완료
                {currentCount > 0 &&
                  ` (현재 +${(currentCount * missionRate).toFixed(
                    1
                  )}%p 적용중)`}
              </ProgressText>
            </ProgressContainer>

            <InfoCard>
              <InfoTitle>혜택 안내</InfoTitle>
              <InfoContent>
                • 우대금리 혜택{"\n"}- 1회 인증마다:{" "}
                <HighlightText teamColor={teamColor.primary}>
                  {missionRate.toFixed(1)}%p 추가 우대금리
                </HighlightText>
                {"\n"}- 최대 {maxCount}회까지 인증 가능:{" "}
                <HighlightText teamColor={teamColor.primary}>
                  최대 {(maxCount * missionRate).toFixed(1)}%p 추가 우대금리
                </HighlightText>
                {"\n\n"}• 인증 가능 티켓:{"\n"}- 경기 일자, 팀명, 좌석번호가
                표시된 실물 티켓
                {"\n"}- 전자티켓 캡처 화면{"\n\n"}• 인증 기간: 2025 KBO 정규시즌
                기간
              </InfoContent>
            </InfoCard>

            <UploadCard>
              <UploadTitle>티켓 사진 업로드</UploadTitle>
              {selectedImage ? (
                <SelectedImage
                  source={{ uri: selectedImage }}
                  resizeMode="cover"
                />
              ) : (
                <UploadArea
                  teamColor={teamColor.primary}
                  onPress={handleSelectImage}
                >
                  <Ionicons name="camera" size={40} color={teamColor.primary} />
                  <UploadPlaceholderText>
                    티켓 사진을 선택해주세요.{"\n"} 경기 정보와 좌석 번호가
                    명확히 보이도록 촬영해주세요.
                  </UploadPlaceholderText>
                </UploadArea>
              )}
              <SubmitButton
                teamColor={teamColor.primary}
                onPress={handleSelectImage}
                style={{ marginTop: 10, marginBottom: 0 }}
              >
                <SubmitButtonText>
                  {selectedImage ? "다른 사진 선택하기" : "티켓 사진 선택하기"}
                </SubmitButtonText>
              </SubmitButton>
              {selectedImage && verificationStatus === "idle" && (
                <InfoContent style={{ marginTop: 10, textAlign: "center" }}>
                  티켓의 경기 정보와 좌석 번호가 명확히 보이는지 확인 후{"\n"}
                  아래 '티켓 인증하기' 버튼을 눌러주세요.
                </InfoContent>
              )}
            </UploadCard>

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

        <Modal
          animationType="fade"
          transparent={true}
          visible={modalVisible}
          onRequestClose={() => setModalVisible(false)}
          statusBarTranslucent={true}
          {...(Platform.OS === "web" ? { style: { zIndex: 1000 } } : {})}
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
                    {teamName || "선택된 팀"} 경기 티켓 인증이 완료되었습니다.
                    {"\n\n"}
                    현재 {currentCount}/{maxCount}회 인증 완료{"\n\n"}
                    {currentCount === maxCount
                      ? `축하합니다! 최대 ${(maxCount * missionRate).toFixed(
                          1
                        )}%p 우대금리가 적용되었습니다.`
                      : `${(currentCount * missionRate).toFixed(
                          1
                        )}%p 우대금리가 적용되었습니다.${"\n"}${
                          maxCount - currentCount
                        }회 더 인증하면 최대 우대금리가 적용됩니다.`}
                  </>
                ) : (
                  <>
                    티켓 인증에 실패했습니다.{"\n\n"}
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
