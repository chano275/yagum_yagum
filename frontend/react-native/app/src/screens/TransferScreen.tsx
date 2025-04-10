import React, { useState, useEffect } from 'react';
import { View, TextInput, TouchableOpacity, SafeAreaView, Platform, useWindowDimensions, ActivityIndicator, Animated, KeyboardAvoidingView, Alert } from 'react-native';
import styled from 'styled-components/native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/Ionicons';
import { BASE_MOBILE_WIDTH, MAX_MOBILE_WIDTH } from '../constants/layout';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { checkAccountNumber, transferMoney } from '../api/account';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Transfer: undefined;
  TransferComplete: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList, 'Transfer'>;

interface StyledProps {
  width: number;
  insetsTop?: number;
}

const TransferScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  const { width: windowWidth } = useWindowDimensions();
  const [accountNumber, setAccountNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [displayAmount, setDisplayAmount] = useState('');
  const [validationStatus, setValidationStatus] = useState<'idle' | 'checking' | 'success' | 'error'>('idle');
  const [isValidated, setIsValidated] = useState(false);
  const [recipientName, setRecipientName] = useState('');
  const [isTransferring, setIsTransferring] = useState(false);
  const insets = useSafeAreaInsets();

  const width = Platform.OS === 'web' 
    ? BASE_MOBILE_WIDTH 
    : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  useEffect(() => {
    if (!isValidated && accountNumber.length === 16) {
      validateAccount();
    } else if (isValidated && accountNumber.length !== 16) {
      setValidationStatus('idle');
      setIsValidated(false);
    }
  }, [accountNumber, isValidated]);

  const validateAccount = async () => {
    try {
      setValidationStatus('checking');
      const response = await checkAccountNumber(accountNumber);
      
      if (response.BOOL) {
        setValidationStatus('success');
        setIsValidated(true);
        setRecipientName(response.NAME);
      } else {
        setValidationStatus('error');
        setIsValidated(false);
      }
    } catch (error) {
      console.error('계좌번호 확인 중 오류:', error);
      setValidationStatus('error');
      setIsValidated(false);
    }
  };

  const handleAccountNumberChange = (text: string) => {
    const numericValue = text.replace(/[^0-9]/g, '');
    if (numericValue.length <= 16) {
      setAccountNumber(numericValue);
    }
  };

  const handleAmountChange = (text: string) => {
    const numericValue = text.replace(/[^0-9]/g, '');
    setAmount(numericValue);
    
    if (numericValue) {
      const formattedAmount = numericValue.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
      setDisplayAmount(formattedAmount);
    } else {
      setDisplayAmount('');
    }
  };

  const handleTransfer = async () => {
    if (!accountNumber || !amount || !isValidated || isTransferring) return;

    try {
      setIsTransferring(true);
      
      // 숫자만 추출하여 이체 금액으로 변환
      const numericAmount = parseInt(amount.replace(/,/g, ''), 10);
      
      await transferMoney({
        deposit_account_no: accountNumber,
        balance: numericAmount
      });

      navigation.navigate('TransferComplete');
    } catch (error) {
      console.error('이체 중 오류:', error);
      Alert.alert(
        '이체 실패',
        '이체 중 오류가 발생했습니다. 다시 시도해주세요.'
      );
    } finally {
      setIsTransferring(false);
    }
  };

  const renderValidationStatus = () => {
    switch (validationStatus) {
      case 'checking':
        return <ActivityIndicator size="small" color="#2D5BFF" />;
      case 'success':
        return <Icon name="checkmark-circle" size={24} color="#00B050" />;
      case 'error':
        return <Icon name="close-circle" size={24} color="#FF3B30" />;
      default:
        return null;
    }
  };

  const renderInputSection = () => (
    <InputSection>
      <InputWrapper>
        <View style={{ width: '100%' }}>
          <InputLabel>계좌번호</InputLabel>
          <UnderlineInput
            value={accountNumber}
            onChangeText={handleAccountNumberChange}
            keyboardType="number-pad"
            maxLength={16}
          />
        </View>
        <ValidationStatusContainer>
          {renderValidationStatus()}
        </ValidationStatusContainer>
      </InputWrapper>
      
      {isValidated && (
        <View style={{ marginTop: 24, width: '100%' }}>
          <View style={{ width: '100%' }}>
            <InputLabel>금액</InputLabel>
            <UnderlineInput
              value={displayAmount}
              onChangeText={handleAmountChange}
              keyboardType="number-pad"
              placeholder="금액을 입력해주세요"
              placeholderTextColor="#999999"
            />
            <AmountUnit>원</AmountUnit>
          </View>
        </View>
      )}
    </InputSection>
  );

  return (
    <Container>
      <MobileContainer width={width} insetsTop={insets.top}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={{ flex: 1 }}
        >
          <HeaderContainer>
            <BackButton onPress={() => navigation.goBack()}>
              <Icon name="chevron-back" size={24} color="#000" />
            </BackButton>
            <HeaderTitle>
              <BlueText>{recipientName || "누구"}</BlueText>
              <HeaderText>에게 보낼까요?</HeaderText>
            </HeaderTitle>
          </HeaderContainer>

          <ContentContainer>
            {renderInputSection()}
          </ContentContainer>

          <BottomButtonContainer>
            <TransferButton 
              disabled={!accountNumber || !amount || !isValidated || isTransferring}
              onPress={handleTransfer}
            >
              {isTransferring ? (
                <ActivityIndicator color="white" />
              ) : (
                <TransferText>다음</TransferText>
              )}
            </TransferButton>
          </BottomButtonContainer>
        </KeyboardAvoidingView>
      </MobileContainer>
    </Container>
  );
};

const Container = styled.View`
  flex: 1;
  align-items: center;
  background-color: white;
`;

const MobileContainer = styled.View<StyledProps>`
  width: ${({ width }) => width}px;
  max-width: 100%;
  flex: 1;
  align-self: center;
  overflow: hidden;
  position: relative;
  background-color: white;
  padding-top: ${props => props.insetsTop || 0}px;
`;

const HeaderContainer = styled.View`
  padding: 12px 16px 20px 4px;
  margin-top: 4px;
`;

const BackButton = styled.TouchableOpacity`
  width: 48px;
  height: 48px;
  justify-content: center;
  align-items: center;
`;

const HeaderTitle = styled.View`
  flex-direction: row;
  align-items: center;
  margin-top: 14px;
  margin-left: 20px;
`;

const HeaderText = styled.Text`
  font-size: 24px;
  font-weight: 600;
  color: #000000;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BlueText = styled.Text`
  color: #4374D9;
  font-size: 24px;
  font-weight: 600;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const ContentContainer = styled.View`
  flex: 1;
  padding: 0 16px;
  margin-top: 8px;
  margin-left: 4px;
`;

const InputSection = styled.View`
  margin-top: 20px;
`;

const InputWrapper = styled.View`
  flex-direction: row;
  align-items: center;
  position: relative;
  width: 100%;
`;

const ValidationStatusContainer = styled.View`
  width: 24px;
  height: 24px;
  justify-content: center;
  align-items: center;
  position: absolute;
  right: 0;
  bottom: 11px;
`;

const UnderlineInput = styled.TextInput.attrs({
  placeholderTextColor: '#999999',
  selectionColor: '#2D5BFF',
  autoCapitalize: 'none',
  autoCorrect: false
})`
  font-size: 18px;
  padding: 8px 0;
  padding-right: 32px;
  border-bottom-width: 1px;
  border-bottom-color: #CCCCCC;
  width: 100%;
  line-height: 22px;
  outline: none;
  font-family: ${({ theme }) => theme.fonts.regular};
  ${Platform.OS === 'web' && `
    outline: none;
    &:focus {
      outline: none;
    }
  `}
`;

const InputLabel = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-bottom: 8px;
  font-weight: 500;
  font-family: ${({ theme }) => theme.fonts.medium};
`;

const BottomButtonContainer = styled.View`
  width: 100%;
  padding: 0 20px;
  padding-bottom: 20px;
  margin-top: auto;
`;

const TransferButton = styled.TouchableOpacity`
  background-color: #2D5BFF;
  padding: 16px;
  border-radius: 12px;
  align-items: center;
  width: 100%;
  opacity: ${props => props.disabled ? 0.5 : 1};
`;

const TransferText = styled.Text`
  color: white;
  font-size: 16px;
  font-weight: 600;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const AmountUnit = styled.Text`
  position: absolute;
  right: 0;
  bottom: 8px;
  font-size: 18px;
  color: #1A1A1A;
  line-height: 22px;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

export default TransferScreen;