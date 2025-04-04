import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  Platform,
  useWindowDimensions,
  Image,
  Animated,
  Easing,
  ActivityIndicator,
} from 'react-native';
import { useTeam } from '../context/TeamContext';
import styled from 'styled-components/native';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import Header from '../components/Header';
import { useJoin } from '../context/JoinContext';
import { api } from '../api/axios';

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

const HeaderTop = styled.View`
  width: 100%;
  height: 60px;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  background-color: white;
  position: relative;
`;

const BackButton = styled.TouchableOpacity`
  position: absolute;
  left: 14px;
  width: 28px;
  height: 28px;
  justify-content: center;
  align-items: center;
`;

const HeaderTitle = styled.Text`
  font-size: 18px;
  font-weight: 600;
  color: #1A1A1A;
`;

const PageNumber = styled.Text`
  position: absolute;
  right: 24px;
  font-size: 14px;
  color: #666666;
  font-weight: 400;
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
`;

const SubTitle = styled.Text`
  font-size: 14px;
  color: #666666;
  font-weight: 400;
`;

const SearchOverlay = styled(Animated.View)`
  position: absolute;
  top: 44px;
  right: 20px;
  height: 36px;
  background-color: #F5F5F5;
  border-radius: 18px;
  flex-direction: row;
  align-items: center;
  overflow: hidden;
  z-index: 10;
  margin-bottom: 8px;
`;

const SearchInput = styled.TextInput`
  flex: 1;
  height: 36px;
  padding: 0 16px;
  font-size: 15px;
  color: #333333;
  outline-width: 0;
  outline-color: transparent;
  outline-style: none;
`;

const SearchIconBackground = styled.View`
  width: 48px;
  height: 48px;
  background-color: #F5F5F5;
  border-radius: 24px;
  justify-content: center;
  align-items: center;
`;

const SearchButton = styled.TouchableOpacity`
  width: 48px;
  height: 48px;
  justify-content: center;
  align-items: center;
`;

const SearchBackdrop = styled.TouchableOpacity`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9;
`;

const TabContainer = styled.View`
  flexDirection: row;
  padding: 8px 16px 8px 16px;
  justifyContent: center;
  gap: 12px;
`;

const TabButton = styled.TouchableOpacity<{ isSelected: boolean; color: string }>`
  padding: 10px 32px;
  background-color: ${({ isSelected, color }) => isSelected ? color : '#FFF'};
  border-radius: 24px;
  border: 1px solid ${({ isSelected, color }) => isSelected ? color : '#DDD'};
`;

const TabText = styled.Text<{ isSelected: boolean; color: string }>`
  color: ${({ isSelected, color }) => isSelected ? 'white' : color};
  font-size: 15px;
  font-weight: ${({ isSelected }) => isSelected ? '600' : '400'};
`;

const PlayerGrid = styled.View`
  flexDirection: row;
  flexWrap: wrap;
  paddingHorizontal: 16px;
  gap: 8px;
  justifyContent: space-between;
  marginTop: 4px;
`;

interface PlayerCardProps {
  isSelected?: boolean;
  teamColor?: string;
}

const PlayerCard = styled.TouchableOpacity<PlayerCardProps>`
  width: 47%;
  backgroundColor: white;
  borderRadius: 12px;
  padding: 12px;
  alignItems: center;
  borderWidth: 1px;
  borderColor: ${props => props.isSelected ? props.teamColor : '#EEEEEE'};
  marginBottom: 8px;
  ${props => props.isSelected && `
    shadowColor: ${props.teamColor};
    shadowOffset: { width: 0, height: 2 };
    shadowOpacity: 0.3;
    shadowRadius: 4;
    elevation: 4;
  `}
`;

const PlayerImage = styled.Image`
  width: 100%;
  height: 120px;
  borderRadius: 8px;
  marginBottom: 8px;
  resizeMode: contain;
`;

const PlayerInfoContainer = styled.View`
  width: 100%;
  flexDirection: row;
  alignItems: center;
  justifyContent: center;
`;

interface PlayerNumberProps {
  textColor: string;
  isSelected?: boolean;
}

const PlayerNumber = styled.Text<PlayerNumberProps>`
  color: ${props => props.textColor};
  fontSize: 14px;
  fontWeight: ${props => props.isSelected ? '700' : '600'};
  marginRight: 4px;
`;

interface PlayerNameProps {
  isSelected?: boolean;
}

const PlayerName = styled.Text<PlayerNameProps>`
  color: ${props => props.isSelected ? '#000000' : '#333333'};
  fontSize: 15px;
  fontWeight: ${props => props.isSelected ? '700' : '600'};
`;

const PlayerPosition = styled.Text`
  color: #666666;
  fontSize: 13px;
`;

const BottomSection = styled.View`
  padding: 0 20px 16px 20px;
  width: 100%;
  backgroundColor: white;
`;

const SelectButton = styled.TouchableOpacity<{ color: string; disabled?: boolean }>`
  backgroundColor: ${({ color, disabled }) => disabled ? '#CCCCCC' : color};
  padding: 16px;
  borderRadius: 8px;
  alignItems: center;
  marginTop: 8px;
  marginBottom: 16px;
  opacity: ${({ disabled }) => disabled ? 0.7 : 1};
`;

const SelectButtonText = styled.Text`
  color: white;
  fontSize: 18px;
  fontWeight: 900;
`;

const CustomScrollView = styled(Animated.ScrollView)`
  flex: 1;
`;

const ScrollContainer = styled.View`
  flex: 1;
  position: relative;
  marginBottom: 16px;
  backgroundColor: white;
`;

const ScrollIndicator = styled(Animated.View)`
  width: 5;
  backgroundColor: rgba(0, 0, 0, 0.2);
  position: absolute;
  right: 4;
  borderRadius: 3;
  top: 0;
`;

interface PlayerType {
  PLAYER_ID: number;
  PLAYER_NAME: string;
  PLAYER_NUM: string;
  PLAYER_TYPE_ID: number;
  player_type_name: string;
  PLAYER_IMAGE_URL: string;
}

const PlayerSelectScreen = () => {
  const navigation = useNavigation();
  const { width: windowWidth } = useWindowDimensions();
  const [selectedTab, setSelectedTab] = useState('투수');
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [searchText, setSearchText] = useState('');
  const { teamColor, teamId } = useTeam();
  const { updatePlayer } = useJoin();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [players, setPlayers] = useState<PlayerType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const searchWidth = useRef(new Animated.Value(48)).current;
  const scrollIndicatorOpacity = useRef(new Animated.Value(0)).current;
  const scrollIndicatorPosition = useRef(new Animated.Value(0)).current;
  let scrollTimer: NodeJS.Timeout;
  const [scrollViewHeight, setScrollViewHeight] = useState(0);
  const [contentHeight, setContentHeight] = useState(0);
  const [indicatorHeight, setIndicatorHeight] = useState(200);

  const tabs = ['투수', '타자'];

  useEffect(() => {
    const fetchPlayers = async () => {
      if (!teamId) return; // teamId가 0이면 API 호출하지 않음
      
      try {
        setIsLoading(true);
        const response = await api.get(`/api/team/${teamId}/details`);
        console.log('API 응답:', response.data);
        
        if (response.data.players && Array.isArray(response.data.players)) {
          setPlayers(response.data.players);
        } else {
          console.error('선수 데이터 형식이 올바르지 않습니다:', response.data);
        }
      } catch (error) {
        console.error('선수 데이터 로딩 실패:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlayers();
  }, [teamId]);

  // 필터링된 선수 목록
  const filteredPlayers = players.filter(player => {
    const isMatchingType = player.player_type_name === selectedTab;
    const isMatchingSearch = searchText
      ? player.PLAYER_NAME.toLowerCase().includes(searchText.toLowerCase())
      : true;
    return isMatchingType && isMatchingSearch;
  });

  const toggleSearch = () => {
    const toValue = isSearchOpen ? 48 : 340;
    
    Animated.timing(searchWidth, {
      toValue,
      duration: 200,
      useNativeDriver: false,
      easing: Easing.out(Easing.ease)
    }).start();
    
    setIsSearchOpen(!isSearchOpen);
  };

  const showScrollIndicator = () => {
    // 빠르게 나타나고 서서히 사라지는 효과
    Animated.timing(scrollIndicatorOpacity, {
      toValue: 1,
      duration: 150,
      useNativeDriver: true,
      easing: Easing.out(Easing.ease)
    }).start();

    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {
      Animated.timing(scrollIndicatorOpacity, {
        toValue: 0,
        duration: 500, // 사라지는 시간을 늘림
        useNativeDriver: true,
        easing: Easing.inOut(Easing.ease) // 부드러운 이징 효과 추가
      }).start();
    }, 1200); // 표시 시간도 조금 늘림
  };

  const handleScroll = (event: any) => {
    const { contentOffset, contentSize, layoutMeasurement } = event.nativeEvent;
    
    // 스크롤 가능한 전체 높이 계산
    const scrollableHeight = contentSize.height - layoutMeasurement.height;
    
    if (scrollableHeight <= 0) return;

    // 스크롤 인디케이터가 이동할 수 있는 최대 거리 계산
    const indicatorMaxScroll = layoutMeasurement.height - indicatorHeight;
    
    // 현재 스크롤 위치의 비율을 계산하여 인디케이터 위치 설정
    const scrollPercentage = contentOffset.y / scrollableHeight;
    const indicatorPosition = scrollPercentage * indicatorMaxScroll;
    
    scrollIndicatorPosition.setValue(Math.max(0, Math.min(indicatorPosition, indicatorMaxScroll)));
    showScrollIndicator();
  };

  const handleLayout = (event: any) => {
    const height = event.nativeEvent.layout.height;
    setScrollViewHeight(height);
    
    if (contentHeight > 0) {
      // 스크롤바를 무조건 크게 설정 (컨텐츠가 적으므로)
      setIndicatorHeight(Math.max(height * 0.8, 200));
    }
  };

  const handleContentSizeChange = (width: number, height: number) => {
    setContentHeight(height);
    
    if (scrollViewHeight > 0) {
      // 컨텐츠 양에 따라 동적으로 스크롤바 길이 조정
      const visibleRatio = scrollViewHeight / height;
      
      // 컨텐츠가 적으면(visibleRatio가 크면) 스크롤바가 길어짐
      if (visibleRatio > 0.8) {
        // 컨텐츠가 매우 적은 경우
        setIndicatorHeight(scrollViewHeight * 0.9);
      } else if (visibleRatio > 0.5) {
        // 컨텐츠가 적은 경우
        setIndicatorHeight(scrollViewHeight * 0.7);
      } else if (visibleRatio > 0.3) {
        // 컨텐츠가 보통인 경우
        setIndicatorHeight(scrollViewHeight * 0.5);
      } else {
        // 컨텐츠가 많은 경우
        setIndicatorHeight(scrollViewHeight * 0.3);
      }
    }
  };

  useEffect(() => {
    return () => {
      clearTimeout(scrollTimer);
    };
  }, []);

  return (
    <AppWrapper>
      <MobileContainer width={windowWidth}>
        <Header 
          title="적금 가입"
          step={1}
          totalSteps={4}
          onBack={() => navigation.goBack()}
        />
        <TitleSection>
          <TitleArea>
            <MainTitle>최애 선수 선택</MainTitle>
            <SubTitle>응원하는 선수를 선택하세요.</SubTitle>
          </TitleArea>
          {isSearchOpen && <SearchBackdrop onPress={toggleSearch} />}
          <SearchOverlay style={{ width: searchWidth }}>
            {isSearchOpen && (
              <SearchInput
                placeholder="최애 선수를 검색하세요"
                placeholderTextColor="#999"
                selectionColor="#999"
                underlineColorAndroid="transparent"
                value={searchText}
                onChangeText={setSearchText}
                autoFocus
              />
            )}
            <SearchButton onPress={toggleSearch}>
              <SearchIconBackground>
                <MaterialIcons 
                  name={isSearchOpen ? "close" : "search"} 
                  size={24} 
                  color="#666" 
                />
              </SearchIconBackground>
            </SearchButton>
          </SearchOverlay>
        </TitleSection>

        <TabContainer>
          {tabs.map(tab => (
            <TabButton
              key={tab}
              isSelected={selectedTab === tab}
              color={teamColor.primary}
              onPress={() => setSelectedTab(tab)}
            >
              <TabText isSelected={selectedTab === tab} color={teamColor.primary}>{tab}</TabText>
            </TabButton>
          ))}
        </TabContainer>

        <ScrollContainer>
          <CustomScrollView
            showsVerticalScrollIndicator={false}
            onScroll={handleScroll}
            scrollEventThrottle={16}
            onLayout={handleLayout}
            onContentSizeChange={handleContentSizeChange}
            contentContainerStyle={{
              paddingTop: 8,
              paddingBottom: 16
            }}
          >
            <PlayerGrid>
              {isLoading ? (
                <ActivityIndicator size="large" color={teamColor.primary} />
              ) : (
                filteredPlayers.map(player => (
                  <PlayerCard
                    key={player.PLAYER_ID}
                    onPress={() => setSelectedPlayer(player.PLAYER_ID)}
                    isSelected={selectedPlayer === player.PLAYER_ID}
                    teamColor={teamColor.primary}
                  >
                    <PlayerImage 
                      source={
                        player.PLAYER_IMAGE_URL 
                          ? { uri: player.PLAYER_IMAGE_URL }
                          : require('../../assets/kbo/players/default.png')
                      }
                    />
                    <PlayerInfoContainer>
                      <PlayerNumber 
                        textColor={teamColor.primary}
                        isSelected={selectedPlayer === player.PLAYER_ID}
                      >
                        NO.{player.PLAYER_NUM}
                      </PlayerNumber>
                      <PlayerName isSelected={selectedPlayer === player.PLAYER_ID}>
                        {player.PLAYER_NAME}
                      </PlayerName>
                    </PlayerInfoContainer>
                  </PlayerCard>
                ))
              )}
            </PlayerGrid>
          </CustomScrollView>

          {contentHeight > scrollViewHeight && (
            <ScrollIndicator 
              style={{ 
                opacity: scrollIndicatorOpacity,
                transform: [{ translateY: scrollIndicatorPosition }],
                height: indicatorHeight
              }} 
            />
          )}
        </ScrollContainer>

        <BottomSection>
          <SelectButton
            color={teamColor.primary}
            disabled={!selectedPlayer}
            onPress={() => {
              if (selectedPlayer) {
                const player = players.find(p => p.PLAYER_ID === selectedPlayer);
                if (player) {
                  updatePlayer({
                    id: player.PLAYER_ID,
                    name: player.PLAYER_NAME,
                    number: player.PLAYER_NUM,
                    position: player.player_type_name,
                    teamId: teamId
                  });
                  navigation.navigate('AccountSelectScreen' as never);
                }
              }
            }}
          >
            <SelectButtonText>선택하기</SelectButtonText>
          </SelectButton>
        </BottomSection>
      </MobileContainer>
    </AppWrapper>
  );
};

export default PlayerSelectScreen;

