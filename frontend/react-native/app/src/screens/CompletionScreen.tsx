import React, { useCallback, useMemo } from 'react';
import { View } from 'react-native';
import styled from 'styled-components/native';
import { MaterialIcons } from '@expo/vector-icons';
import { useJoin } from '../context/JoinContext';
import { useTeam } from '../context/TeamContext';
import { Platform } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../navigation/AppNavigator';

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

const AppWrapper = styled.View`
  flex: 1;
  background-color: white;
`;

const MobileContainer = styled.View`
  width: 100%;
  max-width: ${Platform.OS === 'web' ? `${BASE_MOBILE_WIDTH}px` : `${MAX_MOBILE_WIDTH}px`};
  margin: 0 auto;
  padding: 24px;
  align-items: center;
  justify-content: flex-start;
  padding-top: 120px;
`;

const CheckIcon = styled.View<{ color: string }>`
  width: 100px;
  height: 100px;
  border-radius: 50px;
  background-color: ${props => props.color};
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
`;

const Title = styled.Text`
  font-size: 24px;
  font-weight: bold;
  color: #1A1A1A;
  margin-bottom: 24px;
  text-align: center;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const TitleHighlight = styled.Text<{ color: string }>`
  color: ${props => props.color};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const TitleDivider = styled.View`
  width: 100%;
  height: 1px;
  background-color: #DDDDDD;
  margin-bottom: 24px;
`;

const InfoGrid = styled.View`
  width: 100%;
  margin-top: -8px;
`;

const InfoRow = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding-vertical: 12px;
`;

const InfoLabel = styled.Text`
  font-size: 14px;
  color: #666666;
  font-family: ${({ theme }) => theme.fonts.regular};
`;

const InfoValue = styled.Text`
  font-size: 14px;
  color: #1A1A1A;
  font-family: ${({ theme }) => theme.fonts.medium};
`;

const Banner = styled.View<{ backgroundColor: string }>`
  width: 100%;
  padding: 16px 20px;
  background-color: ${props => props.backgroundColor};
  border-radius: 16px;
  margin-bottom: 16px;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  min-height: 80px;
`;

const BannerContent = styled.View`
  flex: 1;
  margin-right: 12px;
`;

const BannerTitle = styled.Text`
  font-size: 12px;
  font-weight: 600;
  color: #1A1A1A;
  line-height: 18px;
  margin-bottom: 8px;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const PredictButton = styled.TouchableOpacity<{ color: string }>`
  background-color: ${props => props.color};
  padding: 8px 16px;
  border-radius: 20px;
  align-items: center;
  justify-content: center;
`;

const PredictButtonText = styled.Text`
  font-size: 14px;
  color: #FFFFFF;
  font-weight: 600;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const TeamLogo = styled.Image`
  width: 52px;
  height: 52px;
  margin-left: 12px;
`;

const Button = styled.TouchableOpacity<{ color: string }>`
  width: 100%;
  padding: 16px;
  background-color: ${props => props.color};
  border-radius: 12px;
  align-items: center;
  margin-top: auto;
  margin-bottom: 16px;
`;

const ButtonText = styled.Text`
  color: white;
  font-size: 18px;
  font-weight: 900;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

const BottomContainer = styled.View`
  width: 100%;
  position: absolute;
  bottom: 24px;
  left: 24px;
  right: 24px;
  max-width: ${Platform.OS === 'web' ? `${BASE_MOBILE_WIDTH - 48}px` : `${MAX_MOBILE_WIDTH - 48}px`};
  margin: 0 auto;
`;

const CompletionScreen = () => {
  const { joinData } = useJoin();
  const { teamColor } = useTeam();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  // 팀 색상의 파스텔 버전 생성 - useMemo로 최적화
  const getPastelColor = useCallback((hexColor: string) => {
    // hex to rgb
    const r = parseInt(hexColor.slice(1, 3), 16);
    const g = parseInt(hexColor.slice(3, 5), 16);
    const b = parseInt(hexColor.slice(5, 7), 16);
    
    // 파스텔화 (색상을 밝고 연하게)
    const pastelR = Math.min(255, r + (255 - r) * 0.6);
    const pastelG = Math.min(255, g + (255 - g) * 0.6);
    const pastelB = Math.min(255, b + (255 - b) * 0.6);
    
    // rgb to hex
    return '#' + 
      Math.round(pastelR).toString(16).padStart(2, '0') +
      Math.round(pastelG).toString(16).padStart(2, '0') +
      Math.round(pastelB).toString(16).padStart(2, '0');
  }, []);

  const pastelTeamColor = useMemo(() => getPastelColor(teamColor.primary), [teamColor.primary, getPastelColor]);
  
  // 메인 페이지로 이동하는 핸들러 함수 - 로딩 없이 즉시 이동
  const handleNavigateToMain = useCallback(() => {
    navigation.navigate('Main');
  }, [navigation]);
  
  // Matchrank 페이지로 이동하는 핸들러
  const handleNavigateToMatchrank = useCallback(() => {
    navigation.navigate('Matchrank');
  }, [navigation]);
  
  // 팀 로고 선택 로직을 useMemo로 최적화
  const teamLogoSource = useMemo(() => {
    if (!joinData.selectedTeam?.name) return null;
    
    switch(joinData.selectedTeam.name) {
      case 'KIA 타이거즈': return require('../../assets/kbo/tigers.png');
      case '삼성 라이온즈': return require('../../assets/kbo/lions.png');
      case 'LG 트윈스': return require('../../assets/kbo/twins.png');
      case '두산 베어스': return require('../../assets/kbo/bears.png');
      case 'KT 위즈': return require('../../assets/kbo/wiz.png');
      case 'SSG 랜더스': return require('../../assets/kbo/landers.png');
      case '롯데 자이언츠': return require('../../assets/kbo/giants.png');
      case '한화 이글스': return require('../../assets/kbo/eagles.png');
      case 'NC 다이노스': return require('../../assets/kbo/dinos.png');
      case '키움 히어로즈': return require('../../assets/kbo/heroes.png');
      default: return null;
    }
  }, [joinData.selectedTeam?.name]);

  return (
    <AppWrapper>
      <MobileContainer>
        <CheckIcon color={teamColor.primary}>
          <MaterialIcons name="check" size={50} color="white" />
        </CheckIcon>
        
        <Title>
          <TitleHighlight color={teamColor.primary}>야금야금</TitleHighlight>
          {' 적금 가입완료'}
        </Title>

        <TitleDivider />

        <InfoGrid>
          <InfoRow>
            <InfoLabel>나의 응원팀</InfoLabel>
            <InfoValue>{joinData.selectedTeam?.name}</InfoValue>
          </InfoRow>
          <InfoRow>
            <InfoLabel>최애 선수</InfoLabel>
            <InfoValue>{joinData.selectedPlayer?.name}</InfoValue>
          </InfoRow>
        </InfoGrid>
      </MobileContainer>

      <BottomContainer>
        <Banner backgroundColor={`${teamColor.primary}15`}>
          <BannerContent>
            <BannerTitle>우리 팀 순위를 맞추면 우대금리를 드려요!</BannerTitle>
            <PredictButton 
              color={teamColor.primary}
              onPress={handleNavigateToMatchrank}
            >
              <PredictButtonText>순위 예측 바로가기</PredictButtonText>
            </PredictButton>
          </BannerContent>
          <TeamLogo 
            source={teamLogoSource}
            resizeMode="contain"
          />
        </Banner>

        <Button 
          color={teamColor.primary} 
          onPress={handleNavigateToMain}
        >
          <ButtonText>완료</ButtonText>
        </Button>
      </BottomContainer>
    </AppWrapper>
  );
};

export default React.memo(CompletionScreen); 