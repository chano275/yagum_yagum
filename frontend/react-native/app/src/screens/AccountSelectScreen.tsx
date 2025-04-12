import React, { useState, useEffect, useRef } from "react";
import {
  ScrollView,
  View,
  Platform,
  Animated,
  Modal,
  TouchableWithoutFeedback,
  ActivityIndicator,
  LayoutAnimation,
  UIManager,
  Easing,
  StatusBar,
} from "react-native";
import styled from "styled-components/native";
import { useNavigation, useRoute } from "@react-navigation/native";
import { useTeam } from "../context/TeamContext";
import { useAccountStore } from "../store/useStore";
import { useStore } from "../store/useStore";
import { useJoin } from "../context/JoinContext";
import { UserAccountsResponse, SourceAccount } from "../types/account";
import Header from "../components/Header";
import { MaterialIcons } from "@expo/vector-icons";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { RootStackParamList } from "../navigation/AppNavigator";
import axios from "axios";
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { StatusBar as ExpoStatusBar } from 'expo-status-bar';
import TermsModal from "../components/TermsModal";
import PrivacyModal from "../components/PrivacyModal";
import MarketingModal from "../components/MarketingModal";

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// BaseStyledProps 정의 (선택적 width)
interface BaseStyledProps {
  width?: number;
}

// 확장된 StyledProps (insetsTop 포함)
interface StyledProps extends BaseStyledProps {
  insetsTop?: number;
  insetsBottom?: number;
  color?: string;
  isSelected?: boolean;
  disabled?: boolean;
}

const AppWrapper = styled.View`
  flex: 1;
  align-items: center;
  width: 100%;
  background-color: white;
`;

const MobileContainer = styled.View<StyledProps>`
  width: ${Platform.OS === "web"
    ? `${BASE_MOBILE_WIDTH}px`
    : `${MAX_MOBILE_WIDTH}px`};
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
  padding-top: ${props => props.insetsTop || 0}px;
`;

const TitleSection = styled.View`
  padding: 20px 20px 24px 20px;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
`;

const TitleArea = styled.View`
  flex: 1;
`;

const MainTitle = styled.Text`
  font-size: 16px;
  font-weight: 600;
  color: #333333;
  margin-bottom: 8px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const SubTitle = styled.Text`
  font-size: 14px;
  color: #666666;
  font-weight: 400;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const Content = styled.View`
  flex: 1;
  padding: 0 20px;
`;

const Section = styled.View`
  margin-bottom: 32px;
`;

const AgreementCard = styled.View`
  background-color: #f8f8fa;
  border-radius: 16px;
  padding: 20px;
  width: 100%;
`;

const AgreementItem = styled.View`
  flex-direction: row;
  align-items: center;
  padding: 16px 0;
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
`;

const AgreementItemLast = styled(AgreementItem)`
  border-bottom-width: 0;
`;

interface CheckBoxProps {
  isChecked: boolean;
  color: string;
}

const CheckBox = styled.TouchableOpacity<CheckBoxProps>`
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border-width: 1.5px;
  border-color: ${(props) => (props.isChecked ? props.color : "#CCCCCC")};
  background-color: ${(props) => (props.isChecked ? props.color : "white")};
  justify-content: center;
  align-items: center;
  margin-right: 12px;
`;

const CheckIcon = styled.View`
  width: 10px;
  height: 6px;
  border-left-width: 2px;
  border-bottom-width: 2px;
  border-color: white;
  transform: rotate(-45deg);
  margin-top: -2px;
`;

const AgreementTextAll = styled.Text`
  flex: 1;
  font-size: 16px;
  font-weight: 700;
  color: #1b1d1f;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const AgreementText = styled.Text`
  flex: 1;
  font-size: 14px;
  color: #666666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ViewButton = styled.TouchableOpacity`
  padding: 4px 8px;
`;

const ViewButtonText = styled.Text`
  font-size: 12px;
  color: #666666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const AccountSection = styled(Section)`
  margin-top: 24px;
`;

const AccountSelect = styled.TouchableOpacity`
  background-color: white;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 12px;
  margin-top: 16px;
`;

const AccountPlaceholder = styled.Text`
  font-size: 16px;
  color: #999999;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const AccountDropdown = styled(Animated.View)`
  background-color: white;
  margin-top: 4px;
  z-index: 9999;
  overflow: hidden;
  ${Platform.OS === "web" &&
  `
    box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
  `}
`;

const AccountDropdownContent = styled.View`
  max-height: 200px;
`;

const AccountInfo = styled.View`
  flex: 1;
`;

const AccountName = styled.Text`
  font-size: 15px;
  color: #333333;
  font-weight: 600;
  margin-bottom: 4px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const AccountNumber = styled.Text`
  font-size: 14px;
  color: #666666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const AccountIcon = styled.View<{ color: string }>`
  width: 32px;
  height: 32px;
  border-radius: 16px;
  background-color: ${(props) => props.color}10;
  justify-content: center;
  align-items: center;
  margin-right: 12px;
`;

const AccountRow = styled.View`
  flex-direction: row;
  align-items: center;
  flex: 1;
`;

const AccountSelectText = styled.Text`
  font-size: 16px;
  color: #666666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

interface SelectButtonProps {
  disabled: boolean;
  color: string;
}

const BottomSection = styled.View<StyledProps>`
  padding: 0 20px ${props => props.insetsBottom || 16}px 20px;
  width: 100%;
  background-color: white;
`;

const SelectButton = styled.TouchableOpacity<SelectButtonProps>`
  background-color: ${(props) => (props.disabled ? "#CCCCCC" : props.color)};
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  margin-top: 8px;
  margin-bottom: 16px;
  opacity: ${(props) => (props.disabled ? 0.7 : 1)};
`;

const SelectButtonText = styled.Text<{ disabled: boolean }>`
  color: white;
  font-size: 18px;
  font-weight: 900;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ModalOverlay = styled.View`
  flex: 1;
  background-color: rgba(0, 0, 0, 0.5);
  justify-content: flex-end;
`;

const ModalContent = styled.View`
  background-color: white;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  padding: 24px 20px;
  max-height: 80%;
`;

const ModalHeader = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.Text`
  font-size: 18px;
  font-weight: 600;
  color: #1b1d1f;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const CloseButton = styled.TouchableOpacity`
  padding: 8px;
`;

const AccountList = styled.ScrollView`
  max-height: 400px;
`;

const AccountOption = styled.TouchableOpacity<{
  isSelected: boolean;
  color: string;
}>`
  flex-direction: row;
  align-items: center;
  padding: 16px;
  background-color: ${(props) =>
    props.isSelected ? props.color + "10" : "white"};
  border-bottom-width: 1px;
  border-bottom-color: #eeeeee;
  &:last-child {
    border-bottom-width: 0;
  }
`;

const LoadingContainer = styled.View`
  padding: 20px;
  align-items: center;
`;

const LoadingText = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-top: 8px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const ErrorContainer = styled.View`
  padding: 16px;
  margin: 16px 0;
  background-color: #FFF2F2;
  border: 1px solid #FFCACA;
  border-radius: 8px;
  align-items: center;
`;

const ErrorText = styled.Text`
  font-size: 14px;
  color: #D33A3A;
  text-align: center;
  line-height: 20px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const RetryButton = styled.TouchableOpacity`
  margin-top: 12px;
  padding: 8px 16px;
  background-color: #F8F8F8;
  border-radius: 6px;
  border: 1px solid #E0E0E0;
`;

const RetryButtonText = styled.Text`
  font-size: 14px;
  color: #333333;
  font-weight: 500;
  font-family: ${({ theme }) => theme.fonts.medium};
`;

const AnimatedSection = styled(Animated.View)`
  overflow: hidden;
`;

const AccountSelectScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute();
  const { teamColor } = useTeam();
  const { accountInfo, isLoading, error, fetchAccountInfo } = useAccountStore();
  const { isLoggedIn, token } = useStore();
  const { updateSourceAccount, joinData, getDBData, applyRuleIdMapping } = useJoin();
  const [agreements, setAgreements] = useState({
    all: false,
    terms: false,
    privacy: false,
    marketing: false,
  });
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isRequiredAgreedPrev, setIsRequiredAgreedPrev] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);
  const expandAnimation = useRef(new Animated.Value(0)).current;
  const opacityAnimation = useRef(new Animated.Value(0)).current;
  const dropdownAnimation = useRef(new Animated.Value(0)).current;
  const insets = useSafeAreaInsets();
  const [isTermsModalVisible, setIsTermsModalVisible] = useState(false);
  const [isPrivacyModalVisible, setIsPrivacyModalVisible] = useState(false);
  const [isMarketingModalVisible, setIsMarketingModalVisible] = useState(false);
  const [containerWidth, setContainerWidth] = useState(Platform.OS === "web" ? BASE_MOBILE_WIDTH : MAX_MOBILE_WIDTH);

  useEffect(() => {
    console.log("로그인 상태:", isLoggedIn);
    console.log("토큰:", token);
    console.log("API 베이스 URL:", process.env.REACT_APP_API_URL);
    fetchAccountInfo();
  }, []);

  useEffect(() => {
    if (accountInfo) {
      console.log("계좌 정보:", accountInfo);
      console.log("출금 계좌:", accountInfo.source_account);
    }
    if (error) {
      console.log("계좌 정보 조회 에러:", error);
    }
  }, [accountInfo, error]);

  const handleAgreementCheck = (key: keyof typeof agreements) => {
    if (key === "all") {
      const newValue = !agreements.all;
      setAgreements({
        all: newValue,
        terms: newValue,
        privacy: newValue,
        marketing: newValue,
      });
      if (newValue) {
        scrollToAccountSection();
      }
    } else {
      const newAgreements = {
        ...agreements,
        [key]: !agreements[key],
      };
      const newAll =
        newAgreements.terms && newAgreements.privacy && newAgreements.marketing;
      setAgreements({
        ...newAgreements,
        all: newAll,
      });
      if (newAgreements.terms && newAgreements.privacy) {
        scrollToAccountSection();
      }
    }
  };

  const isRequiredAgreed = agreements.terms && agreements.privacy;
  const canProceed = isRequiredAgreed && selectedAccount !== null;

  const handleAccountSelect = (accountNumber: string) => {
    setSelectedAccount(accountNumber);
    setIsDropdownOpen(false);
  };

  const scrollToAccountSection = () => {
    setTimeout(() => {
      scrollViewRef.current?.scrollTo({
        y: 500,
        animated: true,
      });
    }, 350); // 애니메이션 완료 후 스크롤
  };

  // 애니메이션 설정
  useEffect(() => {
    if (isRequiredAgreed !== isRequiredAgreedPrev) {
      setIsRequiredAgreedPrev(isRequiredAgreed);

      if (isRequiredAgreed) {
        // 새로운 섹션이 나타날 때
        Animated.parallel([
          Animated.timing(expandAnimation, {
            toValue: 1,
            duration: 300,
            easing: Easing.out(Easing.ease),
            useNativeDriver: false,
          }),
          Animated.timing(opacityAnimation, {
            toValue: 1,
            duration: 350,
            easing: Easing.out(Easing.ease),
            useNativeDriver: true,
          }),
        ]).start(() => {
          scrollToAccountSection(); // 애니메이션 완료 후 스크롤
        });
      } else {
        // 섹션이 사라질 때
        Animated.parallel([
          Animated.timing(expandAnimation, {
            toValue: 0,
            duration: 250,
            easing: Easing.in(Easing.ease),
            useNativeDriver: false,
          }),
          Animated.timing(opacityAnimation, {
            toValue: 0,
            duration: 200,
            easing: Easing.in(Easing.ease),
            useNativeDriver: true,
          }),
        ]).start();
      }
    }
  }, [isRequiredAgreed]);

  const animateDropdown = (toValue: number) => {
    Animated.timing(dropdownAnimation, {
      toValue,
      duration: 250,
      easing: Easing.bezier(0.4, 0, 0.2, 1),
      useNativeDriver: true,
    }).start();
  };

  const handleDropdownToggle = () => {
    const newIsOpen = !isDropdownOpen;
    setIsDropdownOpen(newIsOpen);
    animateDropdown(newIsOpen ? 1 : 0);
    
    if (newIsOpen) {
      // 드롭다운이 열릴 때만 스크롤
      requestAnimationFrame(() => {
        scrollViewRef.current?.scrollTo({
          y: 500,
          animated: true,
        });
      });
    }
  };

  const handleSubmit = async () => {
    if (canProceed && selectedAccount) {
      try {
        setIsSubmitting(true);
        
        // 선택된 계좌 정보를 JoinContext에 저장
        updateSourceAccount(selectedAccount);
        
        // 규칙 ID 매핑을 적용
        applyRuleIdMapping();
        
        // API 호출용 데이터 가져오기
        const requestData = getDBData();
        
        if (!requestData) {
          return;
        }
        
        // API 호출을 위한 헤더 설정
        const headers = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        };
        
        const response = await axios.post(
          // `http://localhost:8000/api/account/create`,
          // `http://3.38.183.156:8000/api/account/create`,
          `https://j12b206.p.ssafy.io/api/account/create`,
          requestData,
          { 
            headers,
            timeout: 15000
          }
        );
        
        // API 호출 성공 시 완료 페이지로 이동
        navigation.navigate("Completion");
        
      } catch (error) {
        console.error("적금 가입 중 오류:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const renderAccountModal = () => (
    <Modal
      visible={isModalVisible}
      transparent
      animationType="slide"
      onRequestClose={() => setIsModalVisible(false)}
    >
      <TouchableWithoutFeedback onPress={() => setIsModalVisible(false)}>
        <ModalOverlay>
          <TouchableWithoutFeedback>
            <ModalContent>
              <ModalHeader>
                <ModalTitle>출금 계좌 선택</ModalTitle>
                <CloseButton onPress={() => setIsModalVisible(false)}>
                  <MaterialIcons name="close" size={24} color="#1B1D1F" />
                </CloseButton>
              </ModalHeader>
              <AccountList>
                {accountInfo?.source_account && (
                  <AccountOption
                    isSelected={
                      selectedAccount === accountInfo.source_account.account_num
                    }
                    color={teamColor.primary}
                    onPress={() =>
                      handleAccountSelect(
                        accountInfo.source_account.account_num
                      )
                    }
                  >
                    <AccountIcon color={teamColor.primary}>
                      <MaterialIcons
                        name="account-balance"
                        size={18}
                        color={teamColor.primary}
                      />
                    </AccountIcon>
                    <AccountInfo>
                      <AccountName>입출금 통장(자유예금)</AccountName>
                      <AccountNumber>
                        {accountInfo.source_account.account_num}
                      </AccountNumber>
                    </AccountInfo>
                    {selectedAccount ===
                      accountInfo.source_account.account_num && (
                      <MaterialIcons
                        name="check-circle"
                        size={20}
                        color={teamColor.primary}
                      />
                    )}
                  </AccountOption>
                )}
              </AccountList>
            </ModalContent>
          </TouchableWithoutFeedback>
        </ModalOverlay>
      </TouchableWithoutFeedback>
    </Modal>
  );

  const renderAccountContent = () => {
    if (isLoading) {
      return (
        <LoadingContainer>
          <ActivityIndicator size="large" color={teamColor.primary} />
          <LoadingText>계좌 정보를 불러오는 중입니다...</LoadingText>
        </LoadingContainer>
      );
    }

    if (error) {
      return (
        <ErrorContainer>
          <ErrorText>계좌 정보를 불러오는데 실패했습니다.</ErrorText>
          <ErrorText>다시 시도해주세요.</ErrorText>
        </ErrorContainer>
      );
    }

    if (!accountInfo?.source_account) {
      return (
        <ErrorContainer>
          <ErrorText>등록된 출금 계좌가 없습니다.</ErrorText>
          <ErrorText>계좌를 먼저 등록해주세요.</ErrorText>
        </ErrorContainer>
      );
    }

    return (
      <View>
        <AccountSelect onPress={handleDropdownToggle}>
          <AccountRow>
            <AccountIcon color={teamColor.primary}>
              <MaterialIcons
                name="account-balance"
                size={18}
                color={teamColor.primary}
              />
            </AccountIcon>
            {selectedAccount ? (
              <AccountInfo>
                <AccountName>입출금 통장(자유예금)</AccountName>
                <AccountNumber>{selectedAccount}</AccountNumber>
              </AccountInfo>
            ) : (
              <AccountPlaceholder>계좌를 선택해주세요</AccountPlaceholder>
            )}
          </AccountRow>
          <MaterialIcons
            name={isDropdownOpen ? "keyboard-arrow-up" : "keyboard-arrow-down"}
            size={24}
            color="#666666"
          />
        </AccountSelect>

        <AccountDropdown
          style={{
            opacity: dropdownAnimation,
            transform: [
              {
                scaleY: dropdownAnimation.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0.9, 1],
                }),
              },
            ],
            transformOrigin: "top",
          }}
        >
          {isDropdownOpen && (
            <AccountOption
              isSelected={
                selectedAccount === accountInfo.source_account.account_num
              }
              color={teamColor.primary}
              onPress={() =>
                handleAccountSelect(accountInfo.source_account.account_num)
              }
            >
              <AccountIcon color={teamColor.primary}>
                <MaterialIcons
                  name="account-balance"
                  size={18}
                  color={teamColor.primary}
                />
              </AccountIcon>
              <AccountInfo>
                <AccountName>입출금 통장(자유예금)</AccountName>
                <AccountNumber>
                  {accountInfo.source_account.account_num}
                </AccountNumber>
              </AccountInfo>
              {selectedAccount === accountInfo.source_account.account_num && (
                <MaterialIcons
                  name="check-circle"
                  size={20}
                  color={teamColor.primary}
                />
              )}
            </AccountOption>
          )}
        </AccountDropdown>
      </View>
    );
  };

  const renderSubmitStatus = () => {
    if (submitError) {
      return (
        <ErrorContainer>
          <ErrorText>{submitError}</ErrorText>
          <RetryButton onPress={() => {
            setSubmitError(null);
          }}>
            <RetryButtonText>다시 시도하기</RetryButtonText>
          </RetryButton>
        </ErrorContainer>
      );
    }
    
    return null;
  };

  return (
    <AppWrapper>
      <MobileContainer 
        insetsTop={insets.top}
        onLayout={(e) => {
          const { width } = e.nativeEvent.layout;
          setContainerWidth(width);
        }}
      >
        <ExpoStatusBar style="dark" />
        <Header
          title="적금 가입"
          step={4}
          totalSteps={4}
          onBack={() => navigation.goBack()}
        />
        <ScrollView
          ref={scrollViewRef}
          style={{ width: "100%", flex: 1 }}
          contentContainerStyle={{
            paddingBottom: 40,
          }}
          scrollEventThrottle={16}
          nestedScrollEnabled={true}
        >
          <Content>
            <Section>
              <AgreementCard>
                <AgreementItem>
                  <CheckBox
                    isChecked={agreements.all}
                    color={teamColor.primary}
                    onPress={() => handleAgreementCheck("all")}
                  >
                    {agreements.all && <CheckIcon />}
                  </CheckBox>
                  <AgreementTextAll>전체 동의</AgreementTextAll>
                </AgreementItem>

                <AgreementItem>
                  <CheckBox
                    isChecked={agreements.terms}
                    color={teamColor.primary}
                    onPress={() => handleAgreementCheck("terms")}
                  >
                    {agreements.terms && <CheckIcon />}
                  </CheckBox>
                  <AgreementText>(필수) 야금야금 이용약관</AgreementText>
                  <ViewButton onPress={() => setIsTermsModalVisible(true)}>
                    <ViewButtonText>보기</ViewButtonText>
                  </ViewButton>
                </AgreementItem>

                <AgreementItem>
                  <CheckBox
                    isChecked={agreements.privacy}
                    color={teamColor.primary}
                    onPress={() => handleAgreementCheck("privacy")}
                  >
                    {agreements.privacy && <CheckIcon />}
                  </CheckBox>
                  <AgreementText>(필수) 개인정보 수집 및 이용 동의</AgreementText>
                  <ViewButton onPress={() => setIsPrivacyModalVisible(true)}>
                    <ViewButtonText>보기</ViewButtonText>
                  </ViewButton>
                </AgreementItem>

                <AgreementItemLast>
                  <CheckBox
                    isChecked={agreements.marketing}
                    color={teamColor.primary}
                    onPress={() => handleAgreementCheck("marketing")}
                  >
                    {agreements.marketing && <CheckIcon />}
                  </CheckBox>
                  <AgreementText>(선택) 마케팅 정보 수신 동의</AgreementText>
                  <ViewButton onPress={() => setIsMarketingModalVisible(true)}>
                    <ViewButtonText>보기</ViewButtonText>
                  </ViewButton>
                </AgreementItemLast>
              </AgreementCard>
            </Section>

            <AnimatedSection
              style={{
                opacity: opacityAnimation,
                transform: [
                  {
                    translateY: expandAnimation.interpolate({
                      inputRange: [0, 1],
                      outputRange: [-20, 0],
                    }),
                  },
                ],
              }}
            >
              <Section>
                <MainTitle>출금계좌</MainTitle>
                <SubTitle>출금할 계좌를 선택해주세요.</SubTitle>
                {renderAccountContent()}
              </Section>
            </AnimatedSection>

            {renderSubmitStatus()}
          </Content>
        </ScrollView>

        <BottomSection insetsBottom={insets.bottom}>
          <SelectButton
            color={teamColor.primary}
            disabled={!canProceed || isSubmitting}
            onPress={handleSubmit}
          >
            {isSubmitting ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <SelectButtonText disabled={!canProceed || isSubmitting}>
                선택
              </SelectButtonText>
            )}
          </SelectButton>
        </BottomSection>

        {renderAccountModal()}
        <TermsModal 
          isVisible={isTermsModalVisible}
          onClose={() => setIsTermsModalVisible(false)}
          width={containerWidth}
        />
        <PrivacyModal 
          isVisible={isPrivacyModalVisible}
          onClose={() => setIsPrivacyModalVisible(false)}
          width={containerWidth}
        />
        <MarketingModal 
          isVisible={isMarketingModalVisible}
          onClose={() => setIsMarketingModalVisible(false)}
          width={containerWidth}
        />
      </MobileContainer>
    </AppWrapper>
  );
};

export default AccountSelectScreen;
