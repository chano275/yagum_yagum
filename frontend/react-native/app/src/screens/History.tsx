import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, Platform, useWindowDimensions, Image } from 'react-native';
import styled from 'styled-components/native';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/Ionicons';
import { LinearGradient } from 'expo-linear-gradient';
import { BASE_MOBILE_WIDTH, MAX_MOBILE_WIDTH } from '../constants/layout';
import { useJoin } from '../context/JoinContext';
import { useAccount } from '../context/AccountContext';
import { getTransactionHistory } from '../api/account';
import { TransactionHistory } from '../types/account';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// 스타일드 컴포넌트용 인터페이스
interface BaseStyledProps {
  width: number;
}

interface StyledProps extends BaseStyledProps {
  insetsTop?: number;
}

// 날짜 포맷팅 함수
const formatDate = (dateStr: string) => {
  if (dateStr.length === 8) {
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    return `${year}.${month}.${day}`;
  }
  return dateStr;
};

const History = () => {
  const navigation = useNavigation();
  const { width: windowWidth } = useWindowDimensions();
  const { joinData } = useJoin();
  const { balance, accountNumber } = useAccount();
  const [transactions, setTransactions] = useState<TransactionHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const insets = useSafeAreaInsets();
  
  // 모바일 최적화 너비 계산
  const width = Platform.OS === 'web' 
    ? BASE_MOBILE_WIDTH 
    : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const data = await getTransactionHistory();
        setTransactions(data);
      } catch (error) {
        console.error('거래 내역 조회 실패:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  return (
    <Container>
      <MobileContainer width={width} insetsTop={insets.top}>
        <LinearGradient
          colors={["#FFFFFF", "#E6EFFE"]}
          locations={[0.19, 1.0]}
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 0,
            height: 320,
          }}
        />
        <HeaderContainer>
          <BackButton onPress={() => navigation.goBack()}>
            <Icon name="chevron-back" size={24} color="#000" />
          </BackButton>
          <HeaderTitle>거래 내역</HeaderTitle>
        </HeaderContainer>

        <ContentContainer>
          <AccountSection>
            <AccountTopSection>
              <BankLogoContainer>
                <BankLogo source={require('../../assets/shinhan-icon.png')} />
              </BankLogoContainer>
              <AccountInfo>
                <AccountType>입출금통장(저축예금)</AccountType>
                <AccountNumber>신한 {accountNumber}</AccountNumber>
              </AccountInfo>
            </AccountTopSection>

            <BalanceSection>
              <Balance>{balance}</Balance>
              <BalanceLabel>총 계좌잔액 {balance}</BalanceLabel>
            </BalanceSection>

            <TransferButton>
              <TransferText>이체</TransferText>
            </TransferButton>

            <Divider width={width} />
          </AccountSection>

          <TransactionList
            showsVerticalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: insets.bottom + 20 }}
          >
            {transactions.map((transaction) => (
              <TransactionItem key={transaction.transactionDate + transaction.balance}>
                <TransactionLeftSection>
                  <DateText>{formatDate(transaction.transactionDate)}</DateText>
                  <MerchantName>{transaction.summary}</MerchantName>
                </TransactionLeftSection>
                <AmountInfo>
                  <AmountText isDeposit={transaction.transactionType.substring(0, 2) === '입금'}>
                    {transaction.transactionType.substring(0, 2) === '입금' ? '+' : '-'}{transaction.balance}원
                  </AmountText>
                  <TotalAmount>{transaction.afterBalance}원</TotalAmount>
                </AmountInfo>
              </TransactionItem>
            ))}
          </TransactionList>
        </ContentContainer>
      </MobileContainer>
    </Container>
  );
};

// 스타일 컴포넌트
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
  padding-top: ${props => props.insetsTop || 0}px;
`;

const HeaderContainer = styled.View`
  flex-direction: row;
  align-items: center;
  padding: 12px 8px 20px 4px;
  margin-top: 4px;
`;

const BackButton = styled.TouchableOpacity`
  width: 48px;
  height: 48px;
  justify-content: center;
  align-items: center;
  padding-left: 0;
`;

const HeaderTitle = styled.Text`
  font-size: 18px;
  font-weight: 600;
  color: #000000;
  margin-left: -6px;
`;

const ContentContainer = styled.View`
  flex: 1;
`;

const AccountSection = styled.View`
  padding: 0 14px;
  margin-top: 8px;
  margin-bottom: 16px;
`;

const AccountTopSection = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 20px;
`;

const BankLogoContainer = styled.View`
  margin-right: 12px;
`;

const BankLogo = styled.Image`
  width: 40px;
  height: 40px;
`;

const AccountInfo = styled.View`
  flex: 1;
`;

const AccountType = styled.Text`
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1a1a1a;
`;

const AccountNumber = styled.Text`
  color: #666;
  font-size: 14px;
`;

const BalanceSection = styled.View`
  margin-bottom: 24px;
  align-items: flex-end;
`;

const Balance = styled.Text`
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a;
  margin-bottom: 4px;
`;

const BalanceLabel = styled.Text`
  font-size: 13px;
  color: #666;
`;

const TransferButton = styled.TouchableOpacity`
  background-color: #4374D9;
  padding: 14px;
  border-radius: 8px;
  align-self: stretch;
  margin-bottom: 12px;
  margin-top: 8px;
`;

const TransferText = styled.Text`
  color: white;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
`;

const Divider = styled.View<BaseStyledProps>`
  height: 1px;
  background-color: #f0f0f0;
  margin: 0 -12px;
`;

const TransactionList = styled.ScrollView`
  flex: 1;
  margin-top: 24px;
  padding: 0 14px;
`;

const TransactionItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 0;
`;

const TransactionLeftSection = styled.View`
  flex: 1;
`;

const DateText = styled.Text`
  font-size: 14px;
  color: #666;
`;

const MerchantName = styled.Text`
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
`;

const AmountInfo = styled.View`
  flex: 1;
  align-items: flex-end;
`;

const AmountText = styled.Text<{ isDeposit: boolean }>`
  font-size: 16px;
  font-weight: 600;
  color: ${({ isDeposit }) => isDeposit ? '#00B050' : '#FF3B30'};
`;

const TotalAmount = styled.Text`
  font-size: 14px;
  color: #666;
`;

export default History;