import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  Platform,
  useWindowDimensions,
  View,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Animated,
  Text,
  LayoutChangeEvent,
  Dimensions,
  Image,
  Easing
} from 'react-native';
import { useTeam } from '../context/TeamContext';
import styled from 'styled-components/native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { useJoin } from '../context/JoinContext';
import Header from '../components/Header';
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../navigation/AppNavigator';
import Tooltip from '../components/Tooltip';
import axios from 'axios';
import { useStore } from '../store/useStore';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// BaseStyledProps 정의 (width는 필수로 변경)
interface BaseStyledProps {
  width: number;
}

// 확장된 StyledProps (insetsTop 포함)
interface StyledProps extends BaseStyledProps {
  insetsTop?: number;
  // 다른 필요한 프롭들 (예: color, isActive)
  color?: string;
  isActive?: boolean;
}

const AppWrapper = styled.View`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
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
  position: relative;
  padding-top: ${props => props.insetsTop || 0}px;
`;

const TitleSection = styled.View`
  padding: 16px 20px 12px 20px;
`;

const MainTitle = styled.Text`
  font-size: 18px;
  font-weight: 700;
  color: #333333;
`;

const SubTitle = styled.Text`
  font-size: 14px;
  color: #666666;
  font-weight: 400;
  margin-top: 4px;
`;

const ContentContainer = styled.ScrollView`
  flex: 1;
  width: 100%;
  padding: 0 20px;
`;

// 상단 목표 카드 스타일
const GoalCard = styled.View`
  width: 100%;
  margin-bottom: 16px;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  shadow-color: #000;
  shadow-offset: 0px 2px;
  shadow-opacity: 0.05;
  shadow-radius: 4px;
  elevation: 2;
`;

const TeamLogoContainer = styled.View`
  flex-direction: row;
  align-items: center;
  margin-bottom: 12px;
`;

const TeamLogo = styled.Image`
  width: 48px;
  height: 48px;
  border-radius: 24px;
  margin-right: 12px;
`;

const TeamInfoContainer = styled.View`
  flex: 1;
`;

const TeamName = styled.Text`
  font-size: 16px;
  font-weight: 600;
  color: #333333;
`;

const UniformName = styled.Text`
  font-size: 14px;
  color: #666666;
  margin-top: 2px;
`;

const GoalInfo = styled.View`
  padding: 12px 0;
`;

const GoalTitle = styled.Text`
  font-size: 15px;
  font-weight: 600;
  color: #333333;
`;

const GoalValue = styled.Text`
  font-size: 24px;
  font-weight: 700;
  color: ${({ color }: { color: string }) => color};
  margin-top: 4px;
`;

const DailyLimitInfo = styled.View`
  margin-top: 8px;
`;

const DailyLimitText = styled.Text`
  font-size: 13px;
  color: #666666;
`;

const DailyLimitValue = styled.Text`
  font-weight: 600;
  color: ${({ color }: { color: string }) => color};
`;

// 규칙 섹션 카드 스타일
const RuleCard = styled.View<{ isLast?: boolean; isCompact?: boolean }>`
  width: 100%;
  margin-bottom: ${({ isLast }) => isLast ? '0' : '12px'};
  background-color: white;
  border-radius: 12px;
  padding: ${({ isCompact }) => isCompact ? '12px 16px' : '16px'};
  shadow-color: #000;
  shadow-offset: 0px 2px;
  shadow-opacity: 0.05;
  shadow-radius: 4px;
  elevation: 2;
`;

const RuleCardContent = styled.View`
  width: 100%;
`;

const RuleSection = styled.View`
  width: 100%;
`;

// 섹션 내용 애니메이션 컨테이너 추가
const SectionContentContainer = styled(Animated.View)`
  width: 100%;
  overflow: hidden;
`;

const RuleSectionTitle = styled.View`
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${({ isExpanded }: { isExpanded?: boolean }) => isExpanded ? '10px' : '0px'};
  width: 100%;
  padding: ${({ isExpanded }: { isExpanded?: boolean }) => isExpanded ? '2px 0' : '4px 0'};
  min-height: 44px;
`;

const RuleSectionTitleText = styled.Text`
  font-size: 16px;
  font-weight: 600;
  color: #333333;
  padding: 4px 0;
`;

const InfoIcon = styled.TouchableOpacity`
  margin-left: 8px;
  padding: 5px;  /* 터치 영역 확장 */
  min-width: 30px;
  min-height: 30px;
  justify-content: center;
  align-items: center;
`;

const GoalInfoRow = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom-width: 0px;
  border-bottom-color: transparent;
`;

const GoalInfoRowLast = styled(GoalInfoRow)`
  border-bottom-width: 0;
  padding-bottom: 0;
`;

const GoalInfoLabel = styled.Text`
  font-size: 15px;
  color: #333333;
`;

const AmountContainer = styled.View`
  border: 1px solid #EEEEEE;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
`;

const AmountRow = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const AmountRowLast = styled(AmountRow)`
  margin-bottom: 0;
`;

const AmountLabel = styled.Text`
  font-size: 14px;
  color: #666666;
`;

const AmountValue = styled.Text<{ color: string }>`
  font-size: 15px;
  font-weight: 600;
  color: ${({ color }) => color};
`;

const InputContainer = styled.View`
  flex-direction: row;
  align-items: center;
  margin-left: auto;
`;

const StyledInput = styled.TextInput`
  width: 80px;
  height: 40px;
  border: 1px solid #EEEEEE;
  border-radius: 8px;
  padding: 0 12px;
  margin-right: 8px;
  text-align: right;
  font-size: 15px;
  background-color: #FCFCFC;
`;

const WonText = styled.Text`
  font-size: 15px;
  color: #333333;
  margin-right: 12px;
`;

// 커스텀 토글 스위치 컴포넌트
const CustomToggle = styled.TouchableOpacity<{ isEnabled: boolean; color: string }>`
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background-color: ${({ isEnabled, color }) => isEnabled ? `${color}` : '#DDDDDD'};
  position: relative;
  justify-content: center;
`;

const ToggleThumb = styled(Animated.View)`
  width: 20px;
  height: 20px;
  border-radius: 10px;
  background-color: white;
  elevation: 2;
  shadow-color: #000;
  shadow-offset: 0px 1px;
  shadow-opacity: 0.2;
  shadow-radius: 2px;
  position: absolute;
`;

const BottomSection = styled.View`
  padding: 12px 16px 24px 16px;
  width: 100%;
  background-color: white;
  border-top-width: 1px;
  border-top-color: #EEEEEE;
`;

const SelectButton = styled.TouchableOpacity<{ color: string; disabled?: boolean }>`
  background-color: ${({ color, disabled }) => disabled ? '#CCCCCC' : color};
  padding: 16px;
  border-radius: 8px;
  align-items: center;
  width: 100%;
  opacity: ${({ disabled }) => disabled ? 0.7 : 1};
`;

const SelectButtonText = styled.Text`
  color: white;
  font-size: 16px;
  font-weight: 700;
`;

const AnimatedInputContainer = styled(Animated.View)`
  width: 100%;
  overflow: hidden;
  background-color: white;
  box-shadow: none;
  shadow-opacity: 0;
  elevation: 0;
`;

// DB 테이블 구조에 맞는 타입 정의
interface SavingRuleDB {
  SAVING_RULE_ID: number;
  USER_SAVING_ID: number;
  AMOUNT: number;
  IS_ENABLED: boolean;
}

interface SavingRuleTypeDB {
  SAVING_RULE_TYPE_ID: number;
  SAVING_RULE_TYPE_NAME: string;
  details: {
    SAVING_RULE_DETAIL_ID: number;
    PLAYER_TYPE_ID: number | null;
    PLAYER_TYPE_NAME: string | null;
    SAVING_RULE_ID: number;
    RULE_DESCRIPTION: string;
    RECORD_TYPE_ID: number;
    RECORD_NAME: string;
  }[];
}

// API로 전송할 규칙 데이터 타입
interface SavingRuleForAPI {
  SAVING_RULE_DETAIL_ID: number;
  SAVING_RULED_AMOUNT: number;
}

// 정보 아이콘 위치 저장을 위한 인터페이스
interface IconPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

// 토글 타입 정의 추가
type ToggleKeys = 'win' | 'basicHit' | 'basicHomerun' | 'basicScore' | 'basicDoublePlay' | 'basicError' | 'basicSweep' | 
                 'pitcherStrikeout' | 'pitcherWalk' | 'pitcherRun' | 
                 'batterHit' | 'batterHomerun' | 'batterSteal' | 
                 'opponentHit' | 'opponentHomerun' | 'opponentDoublePlay' | 'opponentError';

const RuleSettingScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const route = useRoute();
  const { width: windowWidth } = useWindowDimensions();
  const { teamColor } = useTeam();
  const { joinData, updateSavingRules, updateLimits, applyRuleIdMapping, updateSavingRulesForAPI } = useJoin();
  const { token } = useStore();
  const insets = useSafeAreaInsets();
  
  // 스크롤 위치 추적을 위한 ref와 타임아웃 ref
  const scrollViewRef = useRef(null);
  const tooltipTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [scrollY, setScrollY] = useState(0);
  
  // API 데이터 상태 관리
  const [ruleTypes, setRuleTypes] = useState<SavingRuleTypeDB[]>([]);
  const [isRulesLoading, setIsRulesLoading] = useState(false);
  const [rulesError, setRulesError] = useState<string | null>(null);
  
  // 툴팁 관련 상태
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipText, setTooltipText] = useState('');
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0, width: 0 });
  
  // 각 아이콘의 refs 저장
  const iconRefs = useRef<{[key: string]: React.RefObject<any>}>({
    daily: React.createRef(),
    basic: React.createRef(),
    pitcher: React.createRef(),
    batter: React.createRef(),
    opponent: React.createRef()
  });
  
  // 팀 컬러 객체에서 primary 값 추출 또는 기본값 사용
  const primaryColor = typeof teamColor === 'object' && teamColor.primary ? teamColor.primary : "#D11A6F";
  
  // 적금 목표와 한도 불러오기
  const selectedGoalAmount = joinData.savingGoal || 500000;
  const selectedDailyLimit = joinData.dailyLimit || 5000;
  
  // 팀 정보 가져오기 (없으면 기본값 사용)
  // 로컬 assets 이미지 사용 (require는 상수 경로여야 함)
  const getTeamLogo = () => {
    // 목표 이미지 매핑
    const goalImages: {[key: string]: any} = {
      '500000': require('../../assets/kbo/uniform/giants.png'),
      '1000000': require('../../assets/nextseason.png'),
      '1500000': require('../../assets/season_ticket.png'),
      '3000000': require('../../assets/springcamp.png'),
    };
    
    // 선택한 팀에 맞는 유니폼 이미지 설정
    if (joinData.selectedTeam?.name && joinData.savingGoal === 500000) {
      try {
        if (joinData.selectedTeam.name === 'KIA 타이거즈') {
          goalImages['500000'] = require('../../assets/kbo/uniform/tigers.png');
        } else if (joinData.selectedTeam.name === '삼성 라이온즈') {
          goalImages['500000'] = require('../../assets/kbo/uniform/lions.png');
        } else if (joinData.selectedTeam.name === 'LG 트윈스') {
          goalImages['500000'] = require('../../assets/kbo/uniform/twins.png');
        } else if (joinData.selectedTeam.name === '두산 베어스') {
          goalImages['500000'] = require('../../assets/kbo/uniform/bears.png');
        } else if (joinData.selectedTeam.name === 'KT 위즈') {
          goalImages['500000'] = require('../../assets/kbo/uniform/wiz.png');
        } else if (joinData.selectedTeam.name === 'SSG 랜더스') {
          goalImages['500000'] = require('../../assets/kbo/uniform/landers.png');
        } else if (joinData.selectedTeam.name === '롯데 자이언츠') {
          goalImages['500000'] = require('../../assets/kbo/uniform/giants.png');
        } else if (joinData.selectedTeam.name === '한화 이글스') {
          goalImages['500000'] = require('../../assets/kbo/uniform/eagles.png');
        } else if (joinData.selectedTeam.name === 'NC 다이노스') {
          goalImages['500000'] = require('../../assets/kbo/uniform/dinos.png');
        } else if (joinData.selectedTeam.name === '키움 히어로즈') {
          goalImages['500000'] = require('../../assets/kbo/uniform/heroes.png');
        }
      } catch (error) {
        console.log('유니폼 이미지 로딩 오류:', error);
      }
    }
    
    // 선택한 적금 목표 금액 가져오기
    const selectedGoalAmount = String(joinData.savingGoal || 500000);
    
    // 선택한 목표 금액에 해당하는 이미지 반환
    return goalImages[selectedGoalAmount] || require('../../assets/kbo/uniform/giants.png');
  };
  
  const getPlayerImage = () => {
    // 선수 이미지는 기본 이미지 사용
    return require('../../assets/kbo/players/default.png');
  };
  
  const teamLogo = getTeamLogo();
  const teamName = joinData.selectedTeam?.name || '자이언츠';
  const uniformName = joinData.selectedPlayer?.name || '선수 이름';
  
  // 목표 제목 가져오기
  const getGoalTitle = () => {
    const goalAmount = joinData.savingGoal || 500000;
    const goalTitles: { [key: string]: string } = {
      '500000': '유니폼',
      '1000000': '다음 시즌 직관',
      '1500000': '시즌권',
      '3000000': '스프링캠프'
    };
    return goalTitles[String(goalAmount)] || '유니폼';
  };
  
  const goalTitle = getGoalTitle();
  
  // 적금 규칙 불러오기
  const savedRules = joinData.savingRules || {
    win: { enabled: true, amount: 3000 },
    pitcher: { enabled: false, strikeout: 1000, walk: 500, run: 1000 },
    batter: { enabled: false, hit: 500, homerun: 1000, steal: 500 },
    opponent: { enabled: false, hit: 300, homerun: 1000, doublePlay: 1000, error: 1000 }
  };
  
  // 상태 관리
  const [dailyInput, setDailyInput] = useState(selectedDailyLimit.toString());
  
  // 입력 상태 관리
  const [rules, setRules] = useState({
    win: {
      amount: savedRules?.win?.amount || 3000,
    },
    basic: {
      hit: 300,
      homerun: 1000,
      score: 500,
      doublePlay: 1000,
      error: 1000,
      sweep: 5000,
    },
    pitcher: {
      strikeout: savedRules?.pitcher?.strikeout || 1000,
      walk: savedRules?.pitcher?.walk || 500,
      run: savedRules?.pitcher?.run || 1000,
    },
    batter: {
      hit: savedRules?.batter?.hit || 500,
      homerun: savedRules?.batter?.homerun || 1000,
      steal: savedRules?.batter?.steal || 500,
    },
    opponent: {
      hit: savedRules?.opponent?.hit || 300,
      homerun: savedRules?.opponent?.homerun || 1000,
      doublePlay: savedRules?.opponent?.doublePlay || 1000,
      error: savedRules?.opponent?.error || 1000,
    }
  });
  
  // 토글 상태 관리 수정
  const [toggles, setToggles] = useState<Record<ToggleKeys, boolean>>({
    // 기본 규칙
    win: savedRules.win.enabled,
    basicHit: true,
    basicHomerun: true,
    basicScore: true,
    basicDoublePlay: true,
    basicError: true,
    basicSweep: true,
    
    // 투수 규칙
    pitcherStrikeout: savedRules.pitcher.enabled,
    pitcherWalk: savedRules.pitcher.enabled,
    pitcherRun: savedRules.pitcher.enabled,
    
    // 타자 규칙
    batterHit: savedRules.batter.enabled,
    batterHomerun: savedRules.batter.enabled,
    batterSteal: savedRules.batter.enabled,
    
    // 상대팀 규칙
    opponentHit: savedRules.opponent.enabled,
    opponentHomerun: savedRules.opponent.enabled,
    opponentDoublePlay: savedRules.opponent.enabled,
    opponentError: savedRules.opponent.enabled
  });
  
  // 아코디언 섹션 열림/닫힘 상태 관리
  const [expandedSections, setExpandedSections] = useState({
    basic: true,     // 기본 규칙은 기본적으로 열려있음
    pitcher: false,  // 나머지는 접혀있음
    batter: false,
    opponent: false
  });
  
  // 제출 버튼 비활성화 상태
  const [isSubmitDisabled, setIsSubmitDisabled] = useState(false);
  
  // 애니메이션 값
  const pitcherHeight = useRef(new Animated.Value(toggles.pitcherStrikeout ? 1 : 0)).current;
  const batterHeight = useRef(new Animated.Value(toggles.batterHit ? 1 : 0)).current;
  const opponentHeight = useRef(new Animated.Value(toggles.opponentHit ? 1 : 0)).current;
  
  // 각 아이콘의 위치 정보를 저장하는 상태
  const [iconPositions, setIconPositions] = useState<{[key: string]: IconPosition}>({});
  
  // 선택한 선수의 포지션 확인 (투수/타자)
  const playerPosition = joinData.selectedPlayer?.position || '';
  const isPitcher = playerPosition.includes('투수'); // 포지션 문자열에 '투수'가 포함되어 있는지 확인
  
  // 스크롤 이벤트 핸들러 - NativeScrollEvent 타입을 가진 이벤트를 처리합니다
  const handleScroll = useCallback((event: { nativeEvent: { contentOffset: { y: number } } }) => {
    const offsetY = event.nativeEvent.contentOffset.y;
    setScrollY(offsetY);
    console.log("스크롤 위치:", offsetY);
  }, []);
  
  // 아이콘 레이아웃 변경 이벤트 핸들러
  const handleIconLayout = useCallback((type: string, event: any) => {
    const { x, y, width, height } = event.nativeEvent.layout;
    
    // 아이콘의 절대 위치 저장 (스크롤 오프셋은 handleShowTooltip에서 적용)
    setIconPositions(prev => ({
      ...prev,
      [type]: { x, y, width, height }
    }));
    
    console.log(`아이콘 ${type} 레이아웃:`, { x, y, width, height });
  }, []);
  
  // 툴팁 표시 핸들러 (아이콘의 measureInWindow 사용)
  const handleShowTooltip = (type: string) => {
    console.log(`${type} 툴팁 표시 요청`);
    
    // 이미 활성화된 툴팁이 있으면 닫기
    if (tooltipVisible) {
      setTooltipVisible(false);
      
      // 약간의 딜레이 후에 새 툴팁 표시
      setTimeout(() => {
        showTooltipForType(type);
      }, 100);
      return;
    }
    
    showTooltipForType(type);
  };
  
  // 특정 타입의 툴팁 표시 함수
  const showTooltipForType = (type: string) => {
    // 해당 아이콘의 ref 가져오기
    const iconRef = iconRefs.current[type];
    
    if (!iconRef || !iconRef.current) {
      console.log(`아이콘 ref가 없습니다: ${type}`);
      return;
    }
    
    try {
      // 네이티브 환경에서는 measureInWindow 사용
      iconRef.current.measureInWindow((x: number, y: number, width: number, height: number) => {
        console.log(`아이콘 화면상 위치:`, { x, y, width, height, type });
        
        if (isNaN(x) || isNaN(y) || x < 0 || y < 0) {
          console.error('유효하지 않은 위치 값:', { x, y, width, height });
          // 기본 위치 설정
          const defaultY = 300;
          const defaultX = windowWidth / 2;
          
          setTooltipVisible(true);
          setTooltipText(getTooltipContent(type));
          setTooltipPosition({
            top: defaultY,
            left: defaultX,
            width: 30
          });
          return;
        }
        
        // 아이콘 중앙 위치 계산 (화살표가 가리킬 위치)
        const iconCenterX = x + (width / 2);
        const iconBottomY = y + height;
        
        console.log(`계산된 아이콘 중앙:`, { iconCenterX, iconBottomY });
        
        setTooltipVisible(true);
        setTooltipText(getTooltipContent(type));
        setTooltipPosition({
          top: y,
          left: x,
          width: width
        });
        
        // 5초 후 자동으로 닫기
        if (tooltipTimeoutRef.current) {
          clearTimeout(tooltipTimeoutRef.current);
        }
        
        tooltipTimeoutRef.current = setTimeout(() => {
          setTooltipVisible(false);
        }, 5000);
      });
    } catch (error) {
      console.error('툴팁 위치 측정 오류:', error);
      // 오류 발생 시 기본 위치에 표시
      setTooltipVisible(true);
      setTooltipText(getTooltipContent(type));
      setTooltipPosition({
        top: 300,
        left: windowWidth / 2,
        width: 30
      });
    }
  };
  
  // 토글 애니메이션 관련 코드 수정
  const toggleAnimMap = useRef<{ [key in ToggleKeys]?: Animated.Value }>({});

  // React Native의 애니메이션 설정을 위한 변수 생성
  const [basicHeight] = useState(new Animated.Value(1)); // 기본 규칙은 기본적으로 열려있음

  // useEffect에서 초기화
  useEffect(() => {
    // 초기 모든 토글 애니메이션 값 설정
    (Object.keys(toggles) as ToggleKeys[]).forEach(key => {
      if (!toggleAnimMap.current[key]) {
        toggleAnimMap.current[key] = new Animated.Value(toggles[key] ? 1 : 0);
      }
    });

    // 섹션 애니메이션 값 초기화
    basicHeight.setValue(expandedSections.basic ? 1 : 0);
    pitcherHeight.setValue(expandedSections.pitcher ? 1 : 0);
    batterHeight.setValue(expandedSections.batter ? 1 : 0);
    opponentHeight.setValue(expandedSections.opponent ? 1 : 0);

    return () => {
      if (tooltipTimeoutRef.current) {
        clearTimeout(tooltipTimeoutRef.current);
      }
    };
  }, [toggles]);

  // 토글 변경 핸들러 수정
  const handleToggleChange = (type: ToggleKeys, value: boolean) => {
    setToggles(prev => ({ ...prev, [type]: value }));
    
    // 토글 애니메이션 실행
    const animValue = toggleAnimMap.current[type];
    if (animValue) {
      Animated.spring(animValue, {
        toValue: value ? 1 : 0,
        useNativeDriver: false,
        friction: 7,
        tension: 40
      }).start();
    }
    
    // 기존 애니메이션 코드 유지
    const sectionAnimValue = type === 'pitcherStrikeout' ? pitcherHeight : 
                      type === 'pitcherWalk' ? pitcherHeight : 
                      type === 'pitcherRun' ? pitcherHeight :
                      type === 'batterHit' ? batterHeight : 
                      type === 'batterHomerun' ? batterHeight : 
                      type === 'batterSteal' ? batterHeight : 
                      type === 'opponentHit' ? opponentHeight : 
                      type === 'opponentHomerun' ? opponentHeight : 
                      type === 'opponentDoublePlay' ? opponentHeight : 
                      type === 'opponentError' ? opponentHeight : null;
    
    if (sectionAnimValue) {
      Animated.timing(sectionAnimValue, {
        toValue: value ? 1 : 0,
        duration: 300,
        useNativeDriver: false
      }).start();
    }
  };
  
  // 섹션 펼치기/접기 핸들러 개선
  const toggleSection = (section: 'basic' | 'pitcher' | 'batter' | 'opponent') => {
    // 애니메이션 실행
    const newValue = !expandedSections[section];
    
    // 애니메이션 값 가져오기
    const animValue = 
      section === 'basic' ? basicHeight :
      section === 'pitcher' ? pitcherHeight :
      section === 'batter' ? batterHeight : 
      opponentHeight;
    
    // 애니메이션 설정
    Animated.timing(animValue, {
      toValue: newValue ? 1 : 0,
      duration: newValue ? 300 : 250,  // 닫힐 때 더 빠르게 설정
      easing: Easing.bezier(0.25, 0.1, 0.25, 1),
      useNativeDriver: false
    }).start();
    
    // 상태 업데이트
    setExpandedSections(prev => ({
      ...prev,
      [section]: newValue
    }));
  };
  
  // 툴팁 내용 가져오기
  const getTooltipContent = (type: string): string => {
    switch (type) {
      case 'monthly':
        return '월 한도는 매월 1일 초기화됩니다. 월 한도에 도달하면 더 이상 저축이 되지 않습니다.';
      case 'daily':
        return '일일 한도는 매일 자정에 초기화됩니다. 이 금액을 초과하면 해당 일에는 더 이상 저축이 되지 않습니다.';
      case 'basic':
        return '기본 규칙은 경기 결과에 따라 적용됩니다. 승리 시 설정한 금액만큼 저축됩니다.';
      case 'pitcher':
        return '투수 규칙은 투수 기록(승리, 세이브, 이닝 등)에 따라 저축됩니다. 각 기록별로 금액을 설정할 수 있습니다.';
      case 'batter':
        return '타자 규칙은 타자 기록(안타, 홈런, 타점 등)에 따라 저축됩니다. 각 기록별로 금액을 설정할 수 있습니다.';
      case 'opponent':
        return '상대팀 규칙은 상대팀 기록(삼진, 실점 등)에 따라 저축됩니다. 각 기록별로 금액을 설정할 수 있습니다.';
      default:
        return '';
    }
  };
  
  // 컴포넌트 마운트 시 적금 규칙 목록 조회
  useEffect(() => {
    const fetchSavingRules = async () => {
      setIsRulesLoading(true);
      setRulesError(null);
      
      try {
        // 개발 환경 URL로 고정
        const playerId = joinData.selectedPlayer?.id;
        
        // 선수 ID가 있는 경우 해당 선수 기반으로 규칙 조회
        let url = 
        // `http://localhost:8000/api/saving_rule/rules`
        `http://3.38.183.156:8000/api/saving_rule/rules`;
        if (playerId) {
          url += `?player_id=${playerId}`;
        }
        
        console.log(`적금 규칙 목록 조회 URL: ${url}`);
        
        const headers = token ? {
          'Authorization': `Bearer ${token}`
        } : {};
        
        const response = await axios.get(url, { headers });
        
        if (response.status === 200) {
          console.log('적금 규칙 목록 조회 성공:', response.data);
          setRuleTypes(response.data);
          
          // 응답 데이터를 활용하여 UI에 표시할 규칙 정보 가공
          if (response.data && response.data.length > 0) {
            // 여기서 응답 데이터를 파싱하여 UI에 사용할 수 있습니다
            // 예: 기본 규칙, 투수 규칙, 타자 규칙, 상대팀 규칙 등으로 분류
            console.log(`총 ${response.data.length}개의 규칙 타입이 조회되었습니다.`);
            
            // 각 규칙 타입별 상세 규칙 수 로깅
            response.data.forEach((type: SavingRuleTypeDB) => {
              console.log(`${type.SAVING_RULE_TYPE_NAME}: ${type.details.length}개의 상세 규칙`);
            });
          }
        }
      } catch (error) {
        console.error('적금 규칙 목록 조회 실패:', error);
        setRulesError('적금 규칙 목록을 불러오는데 실패했습니다.');
        
        // API 호출이 실패해도 하드코딩된 기본 규칙을 사용하여 계속 진행
        console.log('하드코딩된 기본 규칙을 사용합니다.');
      } finally {
        setIsRulesLoading(false);
      }
    };
    
    fetchSavingRules();
  }, [joinData.selectedPlayer, token]);
  
  // 제출 핸들러
  const handleSubmit = () => {
    // 규칙 데이터 준비
    const processedRules = {
      win: { 
        enabled: toggles.win, 
        amount: parseInt(rules.win.amount.toString()) || 0 
      },
      basic: {
        enabled: toggles.basicHit || toggles.basicHomerun || toggles.basicScore || toggles.basicDoublePlay || toggles.basicError || toggles.basicSweep,
        hit: toggles.basicHit ? (parseInt(rules.basic.hit.toString()) || 0) : 0,
        homerun: toggles.basicHomerun ? (parseInt(rules.basic.homerun.toString()) || 0) : 0,
        score: toggles.basicScore ? (parseInt(rules.basic.score.toString()) || 0) : 0,
        doublePlay: toggles.basicDoublePlay ? (parseInt(rules.basic.doublePlay.toString()) || 0) : 0,
        error: toggles.basicError ? (parseInt(rules.basic.error.toString()) || 0) : 0,
        sweep: toggles.basicSweep ? (parseInt(rules.basic.sweep.toString()) || 0) : 0
      },
      pitcher: { 
        enabled: isPitcher && (toggles.pitcherStrikeout || toggles.pitcherWalk || toggles.pitcherRun), 
        strikeout: isPitcher && toggles.pitcherStrikeout ? (parseInt(rules.pitcher.strikeout.toString()) || 0) : 0,
        walk: isPitcher && toggles.pitcherWalk ? (parseInt(rules.pitcher.walk.toString()) || 0) : 0,
        run: isPitcher && toggles.pitcherRun ? (parseInt(rules.pitcher.run.toString()) || 0) : 0
      },
      batter: { 
        enabled: !isPitcher && (toggles.batterHit || toggles.batterHomerun || toggles.batterSteal), 
        hit: !isPitcher && toggles.batterHit ? (parseInt(rules.batter.hit.toString()) || 0) : 0,
        homerun: !isPitcher && toggles.batterHomerun ? (parseInt(rules.batter.homerun.toString()) || 0) : 0,
        steal: !isPitcher && toggles.batterSteal ? (parseInt(rules.batter.steal.toString()) || 0) : 0
      },
      opponent: { 
        enabled: toggles.opponentHit || toggles.opponentHomerun || toggles.opponentDoublePlay || toggles.opponentError,
        hit: toggles.opponentHit ? (parseInt(rules.opponent.hit.toString()) || 0) : 0, 
        homerun: toggles.opponentHomerun ? (parseInt(rules.opponent.homerun.toString()) || 0) : 0,
        doublePlay: toggles.opponentDoublePlay ? (parseInt(rules.opponent.doublePlay.toString()) || 0) : 0,
        error: toggles.opponentError ? (parseInt(rules.opponent.error.toString()) || 0) : 0
      }
    };
    
    // 일일 한도 저장
    const dailyLimit = parseInt(dailyInput) || 5000;
    
    // 컨텍스트 업데이트
    updateSavingRules(processedRules);
    updateLimits(dailyLimit, joinData.monthLimit || dailyLimit * 30);
    
    // 서버에서 가져온 규칙을 사용하여 매핑
    if (ruleTypes && ruleTypes.length > 0) {
      console.log("서버에서 가져온 규칙 타입으로 매핑 진행");
      
      const mappedRules: SavingRuleForAPI[] = [];
      
      // 기본 규칙 (승리, 안타, 홈런, 득점, 병살타, 실책, 스윕)
      const basicRuleType = ruleTypes.find(type => type.SAVING_RULE_TYPE_NAME === "기본 규칙");
      if (basicRuleType) {
        // 승리
        if (processedRules.win.enabled && processedRules.win.amount > 0) {
          const winRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "승리" || detail.RULE_DESCRIPTION.includes("승리"));
          if (winRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: winRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.win.amount
            });
          }
        }
        
        // 안타
        if (processedRules.basic.enabled && processedRules.basic.hit > 0) {
          const hitRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "안타" || detail.RULE_DESCRIPTION.includes("안타"));
          if (hitRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: hitRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.basic.hit
            });
          }
        }
        
        // 홈런
        if (processedRules.basic.enabled && processedRules.basic.homerun > 0) {
          const homerunRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "홈런" || detail.RULE_DESCRIPTION.includes("홈런"));
          if (homerunRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: homerunRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.basic.homerun
            });
          }
        }
        
        // 득점
        if (processedRules.basic.enabled && processedRules.basic.score > 0) {
          const scoreRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "득점" || detail.RULE_DESCRIPTION.includes("득점"));
          if (scoreRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: scoreRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.basic.score
            });
          }
        }
        
        // 병살타
        if (processedRules.basic.enabled && processedRules.basic.doublePlay > 0) {
          const doublePlayRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "병살타" || detail.RULE_DESCRIPTION.includes("병살"));
          if (doublePlayRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: doublePlayRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.basic.doublePlay
            });
          }
        }
        
        // 실책
        if (processedRules.basic.enabled && processedRules.basic.error > 0) {
          const errorRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "실책" || detail.RULE_DESCRIPTION.includes("실책"));
          if (errorRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: errorRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.basic.error
            });
          }
        }
        
        // 스윕
        if (processedRules.basic.enabled && processedRules.basic.sweep > 0) {
          const sweepRule = basicRuleType.details.find(detail => 
            detail.RECORD_NAME === "스윕" || detail.RULE_DESCRIPTION.includes("스윕"));
          if (sweepRule) {
            mappedRules.push({
              SAVING_RULE_DETAIL_ID: sweepRule.SAVING_RULE_DETAIL_ID,
              SAVING_RULED_AMOUNT: processedRules.basic.sweep
            });
          }
        }
      }
      
      // 투수 규칙
      if (processedRules.pitcher.enabled) {
        const pitcherRuleType = ruleTypes.find(type => type.SAVING_RULE_TYPE_NAME === "투수");
        if (pitcherRuleType) {
          // 삼진
          if (processedRules.pitcher.strikeout > 0) {
            const strikeoutRule = pitcherRuleType.details.find(detail => 
              detail.RECORD_NAME === "삼진" || detail.RULE_DESCRIPTION.includes("삼진"));
            if (strikeoutRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: strikeoutRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.pitcher.strikeout
              });
            }
          }
          
          // 볼넷
          if (processedRules.pitcher.walk > 0) {
            const walkRule = pitcherRuleType.details.find(detail => 
              detail.RECORD_NAME === "볼넷" || detail.RULE_DESCRIPTION.includes("볼넷"));
            if (walkRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: walkRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.pitcher.walk
              });
            }
          }
          
          // 자책
          if (processedRules.pitcher.run > 0) {
            const runRule = pitcherRuleType.details.find(detail => 
              detail.RECORD_NAME === "자책" || detail.RULE_DESCRIPTION.includes("자책"));
            if (runRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: runRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.pitcher.run
              });
            }
          }
        }
      }
      
      // 타자 규칙
      if (processedRules.batter.enabled) {
        const batterRuleType = ruleTypes.find(type => type.SAVING_RULE_TYPE_NAME === "타자");
        if (batterRuleType) {
          // 안타
          if (processedRules.batter.hit > 0) {
            const hitRule = batterRuleType.details.find(detail => 
              detail.RECORD_NAME === "안타" || detail.RULE_DESCRIPTION.includes("안타"));
            if (hitRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: hitRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.batter.hit
              });
            }
          }
          
          // 홈런
          if (processedRules.batter.homerun > 0) {
            const homerunRule = batterRuleType.details.find(detail => 
              detail.RECORD_NAME === "홈런" || detail.RULE_DESCRIPTION.includes("홈런"));
            if (homerunRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: homerunRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.batter.homerun
              });
            }
          }
          
          // 도루
          if (processedRules.batter.steal > 0) {
            const stealRule = batterRuleType.details.find(detail => 
              detail.RECORD_NAME === "도루" || detail.RULE_DESCRIPTION.includes("도루"));
            if (stealRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: stealRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.batter.steal
              });
            }
          }
        }
      }
      
      // 상대팀 규칙
      if (processedRules.opponent.enabled) {
        const opponentRuleType = ruleTypes.find(type => type.SAVING_RULE_TYPE_NAME === "상대팀");
        if (opponentRuleType) {
          // 안타
          if (processedRules.opponent.hit > 0) {
            const hitRule = opponentRuleType.details.find(detail => 
              detail.RECORD_NAME === "안타" || detail.RULE_DESCRIPTION.includes("안타"));
            if (hitRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: hitRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.opponent.hit
              });
            }
          }
          
          // 홈런
          if (processedRules.opponent.homerun > 0) {
            const homerunRule = opponentRuleType.details.find(detail => 
              detail.RECORD_NAME === "홈런" || detail.RULE_DESCRIPTION.includes("홈런"));
            if (homerunRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: homerunRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.opponent.homerun
              });
            }
          }
          
          // 병살타
          if (processedRules.opponent.doublePlay > 0) {
            const doublePlayRule = opponentRuleType.details.find(detail => 
              detail.RECORD_NAME === "병살타" || detail.RULE_DESCRIPTION.includes("병살"));
            if (doublePlayRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: doublePlayRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.opponent.doublePlay
              });
            }
          }
          
          // 실책
          if (processedRules.opponent.error > 0) {
            const errorRule = opponentRuleType.details.find(detail => 
              detail.RECORD_NAME === "실책" || detail.RULE_DESCRIPTION.includes("실책"));
            if (errorRule) {
              mappedRules.push({
                SAVING_RULE_DETAIL_ID: errorRule.SAVING_RULE_DETAIL_ID,
                SAVING_RULED_AMOUNT: processedRules.opponent.error
              });
            }
          }
        }
      }
      
      // 매핑된 규칙이 있으면 저장
      if (mappedRules.length > 0) {
        updateSavingRulesForAPI(mappedRules);
        console.log('서버 데이터로 매핑된 규칙 정보:', mappedRules);
      } else {
        // 매핑에 실패한 경우 기본 ID 매핑 사용
        console.log('매핑된 규칙이 없어 기본 ID 매핑을 사용합니다.');
        applyRuleIdMapping();
      }
    } else {
      // 서버에서 규칙 정보를 가져오지 못한 경우 기본 ID 매핑 사용
      console.log('서버에서 규칙 정보를 가져오지 못했습니다. 기본 ID 매핑을 사용합니다.');
      applyRuleIdMapping();
    }
    
    // 다음 화면으로 이동
    navigation.navigate('AccountSelect');
  };
  
  const formatAmount = (amount: number) => {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  // 컴포넌트 마운트 시 경고 메시지로 디버깅 정보 출력
  useEffect(() => {
    console.log('RuleSettingScreen 마운트됨, 화면 너비:', windowWidth);
    
    // 모든 아이콘 위치를 주기적으로 로깅 (디버깅용)
    const interval = setInterval(() => {
      if (Object.keys(iconPositions).length > 0) {
        console.log('저장된 아이콘 위치:', iconPositions);
        clearInterval(interval);
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [iconPositions, windowWidth]);

  // 애니메이션 토글 컴포넌트
  const AnimatedToggle = ({ name, isEnabled, color }: { name: ToggleKeys, isEnabled: boolean, color: string }) => {
    // 해당 키에 애니메이션 값이 없을 경우 생성
    if (!toggleAnimMap.current[name]) {
      toggleAnimMap.current[name] = new Animated.Value(isEnabled ? 1 : 0);
    }
    
    // 애니메이션 값 가져오기
    const anim = toggleAnimMap.current[name];
    
    // 토글 스위치 상수 정의
    const TOGGLE_WIDTH = 44;
    const THUMB_WIDTH = 20;
    const PADDING = 2;
    
    // 왼쪽 위치: 패딩과 같음 (PADDING)
    // 오른쪽 위치: 전체 너비 - 썸네일 너비 - 패딩 (TOGGLE_WIDTH - THUMB_WIDTH - PADDING)
    const translateX = anim?.interpolate({
      inputRange: [0, 1],
      outputRange: [PADDING, TOGGLE_WIDTH - THUMB_WIDTH - PADDING]
    });
    
    return (
      <CustomToggle 
        isEnabled={isEnabled} 
        color={color}
        activeOpacity={0.8}
        onPress={() => handleToggleChange(name, !isEnabled)}
      >
        <ToggleThumb 
          style={{ 
            transform: [{ translateX: translateX || 0 }] 
          }} 
        />
      </CustomToggle>
    );
  };

  // 일일한도 입력 처리 함수 추가
  const handleDailyInputChange = (text: string) => {
    const inputValue = parseInt(text) || 0;
    // 선택된 목표의 일일한도를 넘지 않도록 제한
    if (inputValue > selectedDailyLimit) {
      setDailyInput(selectedDailyLimit.toString());
    } else {
      setDailyInput(text);
    }
  };

  return (
    <AppWrapper>
      <StatusBar backgroundColor='transparent' translucent={Platform.OS === 'android'} />
      <MobileContainer width={windowWidth} insetsTop={insets.top}>
        <Header
          title="적금 규칙 설정"
          step={3}
          totalSteps={4}
          onBack={() => navigation.goBack()}
        />
        
        <TitleSection>
          <MainTitle>적금 규칙 설정</MainTitle>
          <SubTitle>
            {isPitcher 
              ? '투수 선수를 선택하셨습니다. 투수 관련 적금 규칙을 설정하세요.' 
              : '타자 선수를 선택하셨습니다. 타자 관련 적금 규칙을 설정하세요.'}
          </SubTitle>
        </TitleSection>

        <ContentContainer 
          showsVerticalScrollIndicator={false} 
          ref={scrollViewRef}
          onScroll={handleScroll}
          scrollEventThrottle={16}
          contentContainerStyle={{ 
            paddingBottom: 20,
            flexGrow: 1 
          }}
        >
          {/* 상단 목표 카드 */}
          <GoalCard>
            <TeamLogoContainer>
              <TeamLogo source={teamLogo} />
              <TeamInfoContainer>
                <TeamName>{goalTitle}</TeamName>
                <View style={{ marginTop: 8 }}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text style={{ fontSize: 14, color: '#666666' }}>목표 금액</Text>
                    <Text style={{ fontSize: 14, fontWeight: '600', color: '#333333' }}>{formatAmount(selectedGoalAmount)}원</Text>
                  </View>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                    <Text style={{ fontSize: 14, color: '#666666' }}>최대 일일 한도</Text>
                    <Text style={{ fontSize: 14, fontWeight: '600', color: '#333333' }}>{formatAmount(parseInt(dailyInput) || 0)}원</Text>
                  </View>
                </View>
              </TeamInfoContainer>
            </TeamLogoContainer>
            
            <View style={{ 
              height: 1, 
              backgroundColor: '#EEEEEE', 
              width: '100%', 
              marginVertical: 12 
            }} />
            
            <View>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#333333', marginBottom: 12 }}>일일 한도 설정</Text>
              
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text style={{ fontSize: 15, color: '#333333' }}>일일 한도</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <StyledInput
                    value={dailyInput}
                    onChangeText={handleDailyInputChange}
                    keyboardType="numeric"
                    maxLength={8}
                    placeholder={`${selectedDailyLimit.toLocaleString()}원`}
                    style={{ 
                      width: 120, 
                      height: 40, 
                      borderWidth: 1, 
                      borderColor: '#EEEEEE',
                      borderRadius: 8, 
                      paddingHorizontal: 12,
                      textAlign: 'right',
                      fontSize: 15
                    }}
                  />
                  <Text style={{ marginLeft: 8, fontSize: 15 }}>원</Text>
                  <InfoIcon 
                    onPress={() => {
                      console.log('Daily icon pressed');
                      handleShowTooltip('daily');
                    }}
                    onLayout={(event) => handleIconLayout('daily', event)}
                    ref={iconRefs.current.daily}
                    style={{ marginLeft: 8 }}
                  >
                    <Ionicons name="information-circle-outline" size={20} color="#999999" />
                  </InfoIcon>
                </View>
              </View>
            </View>
          </GoalCard>

          {/* 기본 규칙 설정 */}
          <RuleCard isCompact={!expandedSections.basic}>
            <RuleCardContent>
              <TouchableOpacity 
                onPress={() => toggleSection('basic')}
                activeOpacity={0.7}
                style={{ width: '100%' }}
              >
                <RuleSectionTitle isExpanded={expandedSections.basic}>
                  <RuleSectionTitleText>기본 규칙 설정</RuleSectionTitleText>
                  <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <InfoIcon 
                      onPress={(e) => {
                        e.stopPropagation();
                        handleShowTooltip('basic');
                      }}
                      onLayout={(event) => handleIconLayout('basic', event)}
                      ref={iconRefs.current.basic}
                    >
                      <Ionicons name="information-circle-outline" size={20} color="#999999" />
                    </InfoIcon>
                    <MaterialIcons 
                      name={expandedSections.basic ? "keyboard-arrow-up" : "keyboard-arrow-down"} 
                      size={24} 
                      color="#666666"
                      style={{ marginLeft: 8 }}
                    />
                  </View>
                </RuleSectionTitle>
              </TouchableOpacity>
              
              <Animated.View style={{
                maxHeight: basicHeight.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0, 1000]
                }),
                opacity: basicHeight,
                overflow: 'hidden',
                transform: [{ 
                  translateY: basicHeight.interpolate({
                    inputRange: [0, 1],
                    outputRange: [-5, 0]
                  })
                }]
              }}>
                <View style={{ opacity: expandedSections.basic ? 1 : 0 }}>
                  <GoalInfoRow>
                    <GoalInfoLabel>승리 시</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.win.amount.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          win: { ...prev.win, amount: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.win}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="win" isEnabled={toggles.win} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>안타</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.basic.hit.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          basic: { ...prev.basic, hit: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.basicHit}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="basicHit" isEnabled={toggles.basicHit} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>홈런</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.basic.homerun.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          basic: { ...prev.basic, homerun: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.basicHomerun}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="basicHomerun" isEnabled={toggles.basicHomerun} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>득점</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.basic.score.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          basic: { ...prev.basic, score: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.basicScore}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="basicScore" isEnabled={toggles.basicScore} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>병살타</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.basic.doublePlay.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          basic: { ...prev.basic, doublePlay: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.basicDoublePlay}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="basicDoublePlay" isEnabled={toggles.basicDoublePlay} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>실책</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.basic.error.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          basic: { ...prev.basic, error: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.basicError}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="basicError" isEnabled={toggles.basicError} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>팀 스윕</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.basic.sweep.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          basic: { ...prev.basic, sweep: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.basicSweep}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="basicSweep" isEnabled={toggles.basicSweep} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                </View>
              </Animated.View>
            </RuleCardContent>
          </RuleCard>

          {/* 투수 규칙 설정 - 투수일 때만 표시 */}
          {isPitcher && (
            <RuleCard isCompact={!expandedSections.pitcher}>
              <RuleCardContent>
                <TouchableOpacity 
                  onPress={() => toggleSection('pitcher')}
                  activeOpacity={0.7}
                  style={{ width: '100%' }}
                >
                  <RuleSectionTitle isExpanded={expandedSections.pitcher}>
                    <RuleSectionTitleText>투수 규칙 설정</RuleSectionTitleText>
                    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                      <InfoIcon 
                        onPress={(e) => {
                          e.stopPropagation();
                          handleShowTooltip('pitcher');
                        }}
                        onLayout={(event) => handleIconLayout('pitcher', event)}
                        ref={iconRefs.current.pitcher}
                      >
                        <Ionicons name="information-circle-outline" size={20} color="#999999" />
                      </InfoIcon>
                      <MaterialIcons 
                        name={expandedSections.pitcher ? "keyboard-arrow-up" : "keyboard-arrow-down"} 
                        size={24} 
                        color="#666666"
                        style={{ marginLeft: 8 }}
                      />
                    </View>
                  </RuleSectionTitle>
                </TouchableOpacity>
                
                <Animated.View style={{
                  maxHeight: pitcherHeight.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0, 300]
                  }),
                  opacity: pitcherHeight,
                  overflow: 'hidden',
                  transform: [{ 
                    translateY: pitcherHeight.interpolate({
                      inputRange: [0, 1],
                      outputRange: [-5, 0]
                    })
                  }]
                }}>
                  <View style={{ opacity: expandedSections.pitcher ? 1 : 0 }}>
                    <GoalInfoRow>
                      <GoalInfoLabel>삼진</GoalInfoLabel>
                      <InputContainer>
                        <StyledInput
                          value={rules.pitcher.strikeout.toString()}
                          onChangeText={(text) => setRules(prev => ({ 
                            ...prev, 
                            pitcher: { ...prev.pitcher, strikeout: parseInt(text) || 0 } 
                          }))}
                          keyboardType="numeric"
                          maxLength={8}
                          editable={toggles.pitcherStrikeout}
                        />
                        <WonText>원</WonText>
                        <AnimatedToggle name="pitcherStrikeout" isEnabled={toggles.pitcherStrikeout} color={primaryColor} />
                      </InputContainer>
                    </GoalInfoRow>
                    
                    <GoalInfoRow>
                      <GoalInfoLabel>볼넷</GoalInfoLabel>
                      <InputContainer>
                        <StyledInput
                          value={rules.pitcher.walk.toString()}
                          onChangeText={(text) => setRules(prev => ({ 
                            ...prev, 
                            pitcher: { ...prev.pitcher, walk: parseInt(text) || 0 } 
                          }))}
                          keyboardType="numeric"
                          maxLength={8}
                          editable={toggles.pitcherWalk}
                        />
                        <WonText>원</WonText>
                        <AnimatedToggle name="pitcherWalk" isEnabled={toggles.pitcherWalk} color={primaryColor} />
                      </InputContainer>
                    </GoalInfoRow>
                    
                    <GoalInfoRowLast>
                      <GoalInfoLabel>자책점</GoalInfoLabel>
                      <InputContainer>
                        <StyledInput
                          value={rules.pitcher.run.toString()}
                          onChangeText={(text) => setRules(prev => ({ 
                            ...prev, 
                            pitcher: { ...prev.pitcher, run: parseInt(text) || 0 } 
                          }))}
                          keyboardType="numeric"
                          maxLength={8}
                          editable={toggles.pitcherRun}
                        />
                        <WonText>원</WonText>
                        <AnimatedToggle name="pitcherRun" isEnabled={toggles.pitcherRun} color={primaryColor} />
                      </InputContainer>
                    </GoalInfoRowLast>
                  </View>
                </Animated.View>
              </RuleCardContent>
            </RuleCard>
          )}

          {/* 타자 규칙 섹션 */}
          {!isPitcher && (
            <RuleCard isCompact={!expandedSections.batter}>
              <RuleCardContent>
                <TouchableOpacity 
                  onPress={() => toggleSection('batter')}
                  activeOpacity={0.7}
                  style={{ width: '100%' }}
                >
                  <RuleSectionTitle isExpanded={expandedSections.batter}>
                    <RuleSectionTitleText>타자 규칙 설정</RuleSectionTitleText>
                    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                      <InfoIcon 
                        onPress={(e) => {
                          e.stopPropagation();
                          handleShowTooltip('batter');
                        }}
                        onLayout={(event) => handleIconLayout('batter', event)}
                        ref={iconRefs.current.batter}
                      >
                        <Ionicons name="information-circle-outline" size={20} color="#999999" />
                      </InfoIcon>
                      <MaterialIcons 
                        name={expandedSections.batter ? "keyboard-arrow-up" : "keyboard-arrow-down"} 
                        size={24} 
                        color="#666666"
                        style={{ marginLeft: 8 }}
                      />
                    </View>
                  </RuleSectionTitle>
                </TouchableOpacity>
                
                <Animated.View style={{
                  maxHeight: batterHeight.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0, 300]
                  }),
                  opacity: batterHeight,
                  overflow: 'hidden',
                  transform: [{ 
                    translateY: batterHeight.interpolate({
                      inputRange: [0, 1],
                      outputRange: [-5, 0]
                    })
                  }]
                }}>
                  <View style={{ opacity: expandedSections.batter ? 1 : 0 }}>
                    <GoalInfoRow>
                      <GoalInfoLabel>안타</GoalInfoLabel>
                      <InputContainer>
                        <StyledInput
                          value={rules.batter.hit.toString()}
                          onChangeText={(text) => setRules(prev => ({ 
                            ...prev, 
                            batter: { ...prev.batter, hit: parseInt(text) || 0 } 
                          }))}
                          keyboardType="numeric"
                          maxLength={8}
                          editable={toggles.batterHit}
                        />
                        <WonText>원</WonText>
                        <AnimatedToggle name="batterHit" isEnabled={toggles.batterHit} color={primaryColor} />
                      </InputContainer>
                    </GoalInfoRow>
                    
                    <GoalInfoRow>
                      <GoalInfoLabel>홈런</GoalInfoLabel>
                      <InputContainer>
                        <StyledInput
                          value={rules.batter.homerun.toString()}
                          onChangeText={(text) => setRules(prev => ({ 
                            ...prev, 
                            batter: { ...prev.batter, homerun: parseInt(text) || 0 } 
                          }))}
                          keyboardType="numeric"
                          maxLength={8}
                          editable={toggles.batterHomerun}
                        />
                        <WonText>원</WonText>
                        <AnimatedToggle name="batterHomerun" isEnabled={toggles.batterHomerun} color={primaryColor} />
                      </InputContainer>
                    </GoalInfoRow>
                    
                    <GoalInfoRow>
                      <GoalInfoLabel>도루</GoalInfoLabel>
                      <InputContainer>
                        <StyledInput
                          value={rules.batter.steal.toString()}
                          onChangeText={(text) => setRules(prev => ({ 
                            ...prev, 
                            batter: { ...prev.batter, steal: parseInt(text) || 0 } 
                          }))}
                          keyboardType="numeric"
                          maxLength={8}
                          editable={toggles.batterSteal}
                        />
                        <WonText>원</WonText>
                        <AnimatedToggle name="batterSteal" isEnabled={toggles.batterSteal} color={primaryColor} />
                      </InputContainer>
                    </GoalInfoRow>
                  </View>
                </Animated.View>
              </RuleCardContent>
            </RuleCard>
          )}

          {/* 상대팀 규칙 설정 */}
          <RuleCard isLast={true} isCompact={!expandedSections.opponent}>
            <RuleCardContent>
              <TouchableOpacity 
                onPress={() => toggleSection('opponent')}
                activeOpacity={0.7}
                style={{ width: '100%' }}
              >
                <RuleSectionTitle isExpanded={expandedSections.opponent}>
                  <RuleSectionTitleText>상대팀 규칙 설정</RuleSectionTitleText>
                  <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <InfoIcon 
                      onPress={(e) => {
                        e.stopPropagation();
                        handleShowTooltip('opponent');
                      }}
                      onLayout={(event) => handleIconLayout('opponent', event)}
                      ref={iconRefs.current.opponent}
                    >
                      <Ionicons name="information-circle-outline" size={20} color="#999999" />
                    </InfoIcon>
                    <MaterialIcons 
                      name={expandedSections.opponent ? "keyboard-arrow-up" : "keyboard-arrow-down"} 
                      size={24} 
                      color="#666666"
                      style={{ marginLeft: 8 }}
                    />
                  </View>
                </RuleSectionTitle>
              </TouchableOpacity>
              
              <Animated.View style={{
                maxHeight: opponentHeight.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0, 300]
                }),
                opacity: opponentHeight,
                overflow: 'hidden',
                transform: [{ 
                  translateY: opponentHeight.interpolate({
                    inputRange: [0, 1],
                    outputRange: [-5, 0]
                  })
                }]
              }}>
                <View style={{ opacity: expandedSections.opponent ? 1 : 0 }}>
                  <GoalInfoRow>
                    <GoalInfoLabel>안타</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.opponent.hit.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          opponent: { ...prev.opponent, hit: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.opponentHit}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="opponentHit" isEnabled={toggles.opponentHit} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>홈런</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.opponent.homerun.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          opponent: { ...prev.opponent, homerun: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.opponentHomerun}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="opponentHomerun" isEnabled={toggles.opponentHomerun} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRow>
                    <GoalInfoLabel>병살타</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.opponent.doublePlay.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          opponent: { ...prev.opponent, doublePlay: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.opponentDoublePlay}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="opponentDoublePlay" isEnabled={toggles.opponentDoublePlay} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRow>
                  
                  <GoalInfoRowLast>
                    <GoalInfoLabel>실책</GoalInfoLabel>
                    <InputContainer>
                      <StyledInput
                        value={rules.opponent.error.toString()}
                        onChangeText={(text) => setRules(prev => ({ 
                          ...prev, 
                          opponent: { ...prev.opponent, error: parseInt(text) || 0 } 
                        }))}
                        keyboardType="numeric"
                        maxLength={8}
                        editable={toggles.opponentError}
                      />
                      <WonText>원</WonText>
                      <AnimatedToggle name="opponentError" isEnabled={toggles.opponentError} color={primaryColor} />
                    </InputContainer>
                  </GoalInfoRowLast>
                </View>
              </Animated.View>
            </RuleCardContent>
          </RuleCard>
        </ContentContainer>
        
        <BottomSection>
          <SelectButton 
            color={primaryColor}
            disabled={isSubmitDisabled}
            onPress={handleSubmit}
          >
            <SelectButtonText>선택</SelectButtonText>
          </SelectButton>
        </BottomSection>
        
        {/* 툴팁 컴포넌트 */}
        <Tooltip
          isVisible={tooltipVisible}
          position={tooltipPosition}
          text={tooltipText}
          onClose={() => setTooltipVisible(false)}
          color={primaryColor}
          autoCloseDelay={5000}
        />
      </MobileContainer>
    </AppWrapper>
  );
};

export default RuleSettingScreen; 