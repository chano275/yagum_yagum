import React, { useState, useRef } from 'react';
import {
  Platform,
  useWindowDimensions,
  Image,
  View,
  TouchableOpacity,
  Animated,
  StyleSheet,
  FlatList,
  Text,
} from 'react-native';
import { useTeam } from '../context/TeamContext';
import styled from 'styled-components/native';
import { useNavigation } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { useJoin } from '../context/JoinContext';
import Header from '../components/Header';
import { MaterialIcons } from '@expo/vector-icons';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../navigation/AppNavigator';

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

const AppWrapper = styled.View`
  flex: 1;
  align-items: center;
  width: 100%;
  background-color: white;
`;

const MobileContainer = styled.View<{ width: number }>`
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
`;

const ContentContainer = styled.View`
  flex: 1;
  padding: 0 16px;
  padding-bottom: 100px;
`;

const TitleSection = styled.View`
  padding: 20px 20px 16px 20px;
`;

const MainTitle = styled.Text`
  font-size: 20px;
  font-weight: 700;
  color: #333333;
  margin-bottom: 8px;
`;

const SubTitle = styled.Text`
  font-size: 14px;
  color: #666666;
  font-weight: 400;
`;

const GridContainer = styled.View`
  flex: 1;
  width: 100%;
`;

const GoalGridItem = styled.TouchableOpacity<{ teamColor: string, isSelected: boolean }>`
  width: 48%;
  aspect-ratio: 0.9;
  margin-bottom: 12px;
  padding: 16px;
  background-color: ${props => props.isSelected ? `${props.teamColor}10` : 'white'};
  border-radius: 16px;
  border: ${props => props.isSelected ? `2px solid ${props.teamColor}` : '1px solid #EEEEEE'};
  align-items: center;
  justify-content: center;
  shadow-color: #000;
  shadow-offset: 0px 2px;
  shadow-opacity: 0.05;
  shadow-radius: 3px;
  elevation: 2;
`;

const GridItemImage = styled.Image`
  width: 60px;
  height: 60px;
  margin-bottom: 12px;
`;

const GoalItemTitle = styled.Text`
  font-size: 15px;
  font-weight: 600;
  color: #333333;
  text-align: center;
`;

const GoalAmount = styled.Text`
  font-size: 16px;
  font-weight: 700;
  color: #333333;
  text-align: center;
`;

// 상세 카드 스타일
const DetailCardContainer = styled(Animated.View)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.95);
  z-index: 10;
`;

const DetailCard = styled.View<{ teamColor: string }>`
  width: 100%;
  padding: 24px;
  background-color: white;
  border-radius: 20px;
  border: 2px solid ${props => props.teamColor};
  shadow-color: #000;
  shadow-offset: 0px 4px;
  shadow-opacity: 0.15;
  shadow-radius: 8px;
  elevation: 6;
`;

const DetailImage = styled.Image`
  width: 100%;
  height: 160px;
  border-radius: 12px;
  margin-bottom: 20px;
`;

const DetailTitle = styled.Text`
  font-size: 24px;
  font-weight: 700;
  color: #333333;
  text-align: center;
  margin-bottom: 8px;
`;

const DetailDescription = styled.Text`
  font-size: 15px;
  color: #666666;
  text-align: center;
  margin-bottom: 20px;
`;

const AmountContainer = styled.View`
  border: 1px solid #EEEEEE;
  border-radius: 12px;
  padding: 0;
  margin-bottom: 24px;
  background-color: #FAFAFA;
  overflow: hidden;
`;

const GoalInfoRow = styled.View<{ last?: boolean; isHighlighted?: boolean }>`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom-width: ${props => props.last ? '0' : '1px'};
  border-bottom-color: #EEEEEE;
  background-color: ${props => props.isHighlighted ? '#F0F8FF' : 'transparent'};
`;

const GoalInfoLabel = styled.Text<{ isHighlighted?: boolean }>`
  font-size: ${props => props.isHighlighted ? '15px' : '14px'};
  font-weight: ${props => props.isHighlighted ? '600' : '400'};
  color: ${props => props.isHighlighted ? '#333333' : '#666666'};
`;

const GoalInfoValue = styled.Text<{ isHighlighted?: boolean }>`
  font-size: ${props => props.isHighlighted ? '18px' : '15px'};
  font-weight: ${props => props.isHighlighted ? '700' : '500'};
  color: ${props => props.isHighlighted ? '#D11A6F' : '#333333'};
  text-align: right;
`;

const DetailButtonsContainer = styled.View`
  width: 100%;
`;

const SelectButton = styled.TouchableOpacity<{ color: string; isPrimary?: boolean; disabled?: boolean }>`
  background-color: ${({ color, isPrimary, disabled }) => 
    disabled ? '#CCCCCC' : (isPrimary ? color : 'white')};
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  margin-top: 8px;
  margin-bottom: 16px;
  opacity: ${({ disabled }) => disabled ? 0.7 : 1};
  border: ${({ color, isPrimary }) => isPrimary ? 'none' : `1px solid ${color}`};
`;

const SelectButtonText = styled.Text<{ isPrimary?: boolean; color: string; disabled?: boolean }>`
  color: ${({ isPrimary, color, disabled }) => isPrimary ? 'white' : color};
  font-size: 18px;
  font-weight: 900;
`;

const BottomSection = styled.View`
  padding: 0 20px 16px 20px;
  width: 100%;
  position: absolute;
  bottom: 0;
  background-color: white;
  border-top-width: 1px;
  border-top-color: #EEEEEE;
`;

const BottomText = styled.Text`
  text-align: center;
  color: #999999;
  font-size: 13px;
  margin-bottom: 8px;
`;

interface SavingsGoalType {
  id: number;
  title: string;
  description: string;
  goalAmount: number;
  monthlyLimit: number;
  dailyLimit: number;
  image: any;
}

// 적금 목표 데이터
const savingsGoals: SavingsGoalType[] = [
  {
    id: 1,
    title: '유니폼',
    description: '응원하는 팀의 유니폼을 구매해보세요!',
    goalAmount: 500000,
    monthlyLimit: 100000,
    dailyLimit: 5000,
    image: require('../../assets/kbo/tigers.png'),
  },
  {
    id: 2,
    title: '다음 시즌 직관',
    description: '다음 시즌에는 직접 경기장에서 응원해보세요!',
    goalAmount: 1000000,
    monthlyLimit: 200000,
    dailyLimit: 10000,
    image: require('../../assets/kbo/lions.png'),
  },
  {
    id: 3,
    title: '시즌권',
    description: '시즌권으로 모든 경기를 놓치지 말고 즐겨보세요!',
    goalAmount: 1500000,
    monthlyLimit: 300000,
    dailyLimit: 15000,
    image: require('../../assets/kbo/twins.png'),
  },
  {
    id: 4,
    title: '스프링캠프',
    description: '선수들의 훈련 현장을 직접 방문해보세요!',
    goalAmount: 3000000,
    monthlyLimit: 500000,
    dailyLimit: 25000,
    image: require('../../assets/kbo/bears.png'),
  },
];

const formatAmount = (amount: number) => {
  return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const SavingsGoalScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const { width: windowWidth } = useWindowDimensions();
  const { teamColor } = useTeam();
  const { updateSavingGoal, updateLimits } = useJoin();
  
  const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  
  const detailCardScale = useRef(new Animated.Value(0.8)).current;
  const detailCardOpacity = useRef(new Animated.Value(0)).current;

  const showDetailCard = (goalId: number) => {
    setSelectedGoalId(goalId);
    setDetailVisible(true);
    
    // 애니메이션 시작
    Animated.parallel([
      Animated.timing(detailCardScale, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(detailCardOpacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const hideDetailCard = () => {
    // 애니메이션 시작
    Animated.parallel([
      Animated.timing(detailCardScale, {
        toValue: 0.8,
        duration: 250,
        useNativeDriver: true,
      }),
      Animated.timing(detailCardOpacity, {
        toValue: 0,
        duration: 250,
        useNativeDriver: true,
      }),
    ]).start(() => {
      setDetailVisible(false);
    });
  };

  const handleSelect = () => {
    if (selectedGoalId === null) return;
    
    const selectedGoal = savingsGoals.find(goal => goal.id === selectedGoalId);
    if (selectedGoal) {
      updateSavingGoal(selectedGoal.goalAmount);
      updateLimits(selectedGoal.dailyLimit, selectedGoal.monthlyLimit);
      navigation.navigate('RuleSetting' as keyof RootStackParamList);
    }
  };

  const renderGridItem = ({ item }: { item: SavingsGoalType }) => (
    <GoalGridItem 
      teamColor={teamColor.primary} 
      isSelected={item.id === selectedGoalId}
      onPress={() => showDetailCard(item.id)}
      activeOpacity={0.7}
    >
      <GridItemImage source={item.image} resizeMode="contain" />
      <GoalItemTitle>{item.title}</GoalItemTitle>
      <GoalAmount>{formatAmount(item.goalAmount)}원</GoalAmount>
    </GoalGridItem>
  );

  return (
    <AppWrapper>
      <StatusBar style="dark" />
      <MobileContainer width={windowWidth}>
        <Header
          title="적금 가입"
          step={2}
          totalSteps={4}
          onBack={() => navigation.goBack()}
        />
        
        <TitleSection>
          <MainTitle>어떤 목표로 적금할까요?</MainTitle>
          <SubTitle>목표를 선택하고 상세 정보를 확인하세요</SubTitle>
        </TitleSection>

        <ContentContainer>
          <GridContainer>
            <FlatList
              data={savingsGoals}
              renderItem={renderGridItem}
              keyExtractor={(item) => item.id.toString()}
              numColumns={2}
              columnWrapperStyle={{ justifyContent: 'space-between' }}
              showsVerticalScrollIndicator={false}
            />
          </GridContainer>
        </ContentContainer>

        {/* 상세 카드 */}
        {detailVisible && selectedGoalId && (
          <DetailCardContainer 
            style={{ 
              opacity: detailCardOpacity,
              transform: [{ scale: detailCardScale }]
            }}
          >
            <DetailCard teamColor={teamColor.primary}>
              {(() => {
                const selectedGoal = savingsGoals.find(goal => goal.id === selectedGoalId);
                if (!selectedGoal) return null;
                
                return (
                  <>
                    <DetailImage source={selectedGoal.image} resizeMode="contain" />
                    <DetailTitle>{selectedGoal.title}</DetailTitle>
                    <DetailDescription>{selectedGoal.description}</DetailDescription>
                    
                    <AmountContainer>
                      <GoalInfoRow isHighlighted={true}>
                        <GoalInfoLabel isHighlighted={true}>목표 금액</GoalInfoLabel>
                        <GoalInfoValue isHighlighted={true}>{formatAmount(selectedGoal.goalAmount)}원</GoalInfoValue>
                      </GoalInfoRow>
                      <GoalInfoRow>
                        <GoalInfoLabel>월 한도</GoalInfoLabel>
                        <GoalInfoValue>{formatAmount(selectedGoal.monthlyLimit)}원</GoalInfoValue>
                      </GoalInfoRow>
                      <GoalInfoRow last>
                        <GoalInfoLabel>최대 일일 한도</GoalInfoLabel>
                        <GoalInfoValue>{formatAmount(selectedGoal.dailyLimit)}원</GoalInfoValue>
                      </GoalInfoRow>
                    </AmountContainer>
                    
                    <DetailButtonsContainer>
                      <SelectButton 
                        color={teamColor.primary} 
                        isPrimary={true}
                        onPress={handleSelect}
                      >
                        <SelectButtonText isPrimary={true} color={teamColor.primary}>
                          이 목표로 적금 시작하기
                        </SelectButtonText>
                      </SelectButton>
                      
                      <SelectButton 
                        color={teamColor.primary}
                        onPress={hideDetailCard}
                      >
                        <SelectButtonText color={teamColor.primary}>
                          다시 선택하기
                        </SelectButtonText>
                      </SelectButton>
                    </DetailButtonsContainer>
                  </>
                );
              })()}
            </DetailCard>
          </DetailCardContainer>
        )}

        <BottomSection>
          {!detailVisible && (
            <>
              <SelectButton 
                color={teamColor.primary}
                isPrimary={true}
                onPress={() => {
                  if (selectedGoalId) handleSelect();
                  else showDetailCard(1); // 기본으로 첫 번째 목표 선택
                }}
              >
                <SelectButtonText isPrimary={true} color={teamColor.primary}>
                  {selectedGoalId ? '이 목표로 적금 시작하기' : '목표 선택하기'}
                </SelectButtonText>
              </SelectButton>
            </>
          )}
        </BottomSection>
      </MobileContainer>
    </AppWrapper>
  );
};

export default SavingsGoalScreen; 