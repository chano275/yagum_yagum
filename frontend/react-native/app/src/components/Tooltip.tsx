import React, { useRef, useEffect, useState } from 'react';
import { View, TouchableWithoutFeedback, Animated, StyleSheet, Dimensions, Platform, Text } from 'react-native';
import styled from 'styled-components/native';

// 기본 모바일 화면 너비 (디자인 기준값)
const BASE_MOBILE_WIDTH = 375;

// 툴팁 컴포넌트 관련 타입 정의
export interface TooltipProps {
  isVisible: boolean;
  text: string;
  position: {
    top: number;
    left: number;
    width: number;
  };
  onClose: () => void;
  color: string;
  autoCloseDelay?: number; // 자동 닫힘 타이머 (ms)
}

// 툴팁 컴포넌트 스타일
const TooltipContainer = styled(Animated.View)<{ color: string }>`
  position: absolute;
  background-color: white;
  border-radius: 12px;
  padding: 16px 20px;
  width: 230px;
  z-index: 9999;
  shadow-color: #000;
  shadow-offset: 0px 4px;
  shadow-opacity: 0.12;
  shadow-radius: 8px;
  elevation: 15;
  border-width: 1px;
  border-color: ${props => props.color};
`;

// 텍스트 스타일
const TooltipText = styled.Text`
  font-size: 14px;
  line-height: 22px;
  color: #333333;
  letter-spacing: 0.2px;
`;

// 강조 텍스트 스타일
const BoldText = styled.Text`
  font-weight: 700;
  color: #333333;
`;

// 위쪽 방향 화살표
const UpArrow = styled(Animated.View)<{ color: string }>`
  position: absolute;
  width: 0;
  height: 0;
  border-left-width: 10px;
  border-right-width: 10px;
  border-bottom-width: 10px;
  border-left-color: transparent;
  border-right-color: transparent;
  border-bottom-color: ${props => props.color};
  border-style: solid;
  z-index: 9998;
`;

// 아래쪽 방향 화살표
const DownArrow = styled(Animated.View)<{ color: string }>`
  position: absolute;
  width: 0;
  height: 0;
  border-left-width: 10px;
  border-right-width: 10px;
  border-top-width: 10px;
  border-left-color: transparent;
  border-right-color: transparent;
  border-top-color: ${props => props.color};
  border-style: solid;
  z-index: 9998;
`;

// 정규식으로 특정 패턴의 텍스트를 강조하는 함수
const formatText = (text: string) => {
  // 숫자와 단위(원, %, 등)를 포함한 패턴 찾기
  const parts = text.split(/(\d{1,3}(,\d{3})*원|\d+%|\d+개당)/g);
  
  return parts.map((part, index) => {
    if (part && part.match(/\d{1,3}(,\d{3})*원|\d+%|\d+개당/)) {
      return <BoldText key={index}>{part}</BoldText>;
    }
    return part;
  });
};

/**
 * 현대적이고 미니멀한 툴팁 컴포넌트
 */
const Tooltip: React.FC<TooltipProps> = ({ 
  isVisible, 
  text, 
  position, 
  onClose, 
  color,
  autoCloseDelay = 5000 // 기본값 5초
}) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.9)).current;
  const [isClosing, setIsClosing] = useState(false);
  
  // 웹 환경인지 체크
  const isWeb = Platform.OS === 'web';
  
  // 타이머 레퍼런스를 저장
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // 애니메이션 동작 함수
  const animateIn = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 280,
        useNativeDriver: false,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 280,
        useNativeDriver: false,
      })
    ]).start();
  };
  
  const animateOut = (callback: () => void) => {
    setIsClosing(true);
    
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: false,
      }),
      Animated.timing(scaleAnim, {
        toValue: 0.9,
        duration: 200,
        useNativeDriver: false,
      })
    ]).start(() => {
      setIsClosing(false);
      callback();
    });
  };
  
  // 툴팁이 표시될 때 애니메이션 시작
  useEffect(() => {
    if (isVisible && !isClosing) {
      // 애니메이션 시작 전에 초기값 설정
      fadeAnim.setValue(0);
      scaleAnim.setValue(0.9);
      animateIn();
      
      // 일정 시간 후 자동 닫기
      if (autoCloseDelay > 0) {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
        }
        timerRef.current = setTimeout(() => {
          handleClose();
        }, autoCloseDelay);
      }
    }
    
    // 컴포넌트 언마운트 시 타이머 정리
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [isVisible, isClosing, autoCloseDelay]);
  
  // 닫기 핸들러
  const handleClose = () => {
    // 이미 닫히는 중이라면 중복 실행 방지
    if (isClosing) return;
    
    // 타이머가 있으면 제거
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    
    animateOut(onClose);
  };
  
  if (!isVisible && !isClosing) {
    return null;
  }
  
  // 화면 크기 가져오기
  const screenWidth = Dimensions.get('window').width;
  const screenHeight = Dimensions.get('window').height;
  
  // 툴팁 크기
  const tooltipWidth = 230; // 화면 밖으로 안나가게 더 축소
  const tooltipHeight = 100;
  
  // 정보 아이콘 정보 가져오기 
  const { top, left, width: iconWidth } = position;
  
  // 웹앱 환경에서 완전히 고정된 위치 사용
  if (isWeb) {
    // 간단하게 top 값으로 아이콘 종류 결정
    const iconType = 
      top < 350 ? 'daily' :
      top < 450 ? 'basic' :
      top < 550 ? 'pitcher' :
      top < 650 ? 'batter' : 'opponent';
    
    // 웹앱 환경의 고정 좌표 - 이미지에서 보이는 위치에 맞게 조정
    // 왼쪽 값을 60으로 하여 화면 안쪽으로 더 배치
    const fixedPositions = {
      daily: { top: 340, left: 60 },
      basic: { top: 435, left: 60 },
      pitcher: { top: 530, left: 60 },
      batter: { top: 600, left: 60 },
      opponent: { top: 680, left: 60 }
    };
    
    // 선택된 아이콘에 따른 고정 위치
    const tooltipPos = fixedPositions[iconType];
    
    // 툴팁 스타일 - 완전 고정 위치 사용
    const tooltipStyle = {
      top: tooltipPos.top,
      left: tooltipPos.left,
      opacity: fadeAnim, 
      transform: [{ scale: scaleAnim }]
    };
    
    return (
      <View style={[styles.overlay, { backgroundColor: 'transparent' }]} pointerEvents="box-none">
        <TouchableWithoutFeedback onPress={handleClose}>
          <View style={styles.touchableArea}>
            {/* 웹앱에서는 화살표를 표시하지 않음 */}
            <TooltipContainer style={tooltipStyle} color={color}>
              <TooltipText>{formatText(text)}</TooltipText>
            </TooltipContainer>
          </View>
        </TouchableWithoutFeedback>
      </View>
    );
  }
  
  // 모바일 환경에서는 기존 방식 유지
  // 아이콘 중앙 x좌표 계산
  const iconCenterX = left + (iconWidth / 2);
  
  // 툴팁 위치 계산 - 기본적으로 아이콘 아래에 표시
  let tooltipTop = top + 30; // 아이콘 아래 여백
  let arrowTop = top + 20; // 화살표 위치
  let direction: 'up' | 'down' = 'up'; // 기본 방향은 위쪽
  
  // 툴팁이 화면 하단을 벗어나는지 체크
  if (tooltipTop + tooltipHeight > screenHeight - 30) {
    // 아이콘 위에 툴팁 표시
    tooltipTop = Math.max(30, top - tooltipHeight - 15);
    arrowTop = top - 10;
    direction = 'down';
  }
  
  // 툴팁 가로 위치 계산 (아이콘 중앙을 기준으로)
  let tooltipLeft = iconCenterX - (tooltipWidth / 2);
  
  // 화면 좌우 경계 체크
  tooltipLeft = Math.max(20, Math.min(screenWidth - tooltipWidth - 20, tooltipLeft));
  
  // 화살표 가로 위치 계산 (항상 아이콘 중앙에 맞춤)
  let arrowLeft = iconCenterX - 10; // 화살표 너비의 절반
  
  // 화살표가 툴팁 영역을 벗어나지 않도록 제한
  if (arrowLeft < tooltipLeft + 20) {
    arrowLeft = tooltipLeft + 20;
  }
  if (arrowLeft > tooltipLeft + tooltipWidth - 20) {
    arrowLeft = tooltipLeft + tooltipWidth - 20;
  }
  
  // 툴팁 스타일
  const tooltipStyle = {
    top: tooltipTop,
    left: tooltipLeft,
    opacity: fadeAnim,
    transform: [{ scale: scaleAnim }]
  };
  
  // 화살표 스타일
  const arrowStyle = {
    top: arrowTop,
    left: arrowLeft,
    opacity: fadeAnim
  };
  
  return (
    <View style={styles.overlay} pointerEvents="box-none">
      <TouchableWithoutFeedback onPress={handleClose}>
        <View style={styles.touchableArea}>
          {direction === 'up' ? (
            <UpArrow style={arrowStyle} color={color} />
          ) : (
            <DownArrow style={arrowStyle} color={color} />
          )}
          <TooltipContainer style={tooltipStyle} color={color}>
            <TooltipText>{formatText(text)}</TooltipText>
          </TooltipContainer>
        </View>
      </TouchableWithoutFeedback>
    </View>
  );
};

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 9999,
    elevation: 9999,
    backgroundColor: 'transparent',
    pointerEvents: 'box-none'
  },
  touchableArea: {
    flex: 1,
    backgroundColor: 'transparent',
  }
});

export default Tooltip; 