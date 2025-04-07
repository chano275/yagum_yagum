import React, { useRef, useEffect, useState } from 'react';
import { View, TouchableWithoutFeedback, Animated, StyleSheet, Dimensions } from 'react-native';
import styled from 'styled-components/native';

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

// 툴팁 컴포넌트 스타일 - 2025 금융 앱 트렌드 반영
const TooltipContainer = styled(Animated.View)<{ color: string }>`
  position: absolute;
  background-color: white;
  border-radius: 14px;
  padding: 16px 20px;
  max-width: 300px;
  z-index: 9999;
  shadow-color: #000;
  shadow-offset: 0px 4px;
  shadow-opacity: 0.12;
  shadow-radius: 8px;
  elevation: 15;
  border-width: 1px;
  border-color: ${props => props.color};
`;

// 텍스트 스타일 개선
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

// 화살표 스타일 개선
const TooltipArrow = styled(Animated.View)<{ color: string }>`
  position: absolute;
  width: 14px;
  height: 14px;
  background-color: white;
  transform: rotate(45deg);
  z-index: 9998;
  elevation: 15;
  border-width: 1px;
  border-color: ${props => props.color};
  border-right-width: 0;
  border-bottom-width: 0;
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
 * 현대적이고 미니멀한 툴팁 컴포넌트 - 2025 금융 앱 트렌드에 맞게 개선
 * 
 * @param isVisible 툴팁 표시 여부
 * @param text 툴팁에 표시할 텍스트
 * @param position 툴팁이 표시될 위치 정보 (top, left, width)
 * @param onClose 툴팁 닫기 이벤트 핸들러
 * @param color 툴팁의 강조 색상 (테두리 색상)
 * @param autoCloseDelay 자동으로 툴팁이 닫힐 시간 (ms)
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
  
  // 타이머 레퍼런스를 저장
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // 화면 너비 가져오기
  const screenWidth = Dimensions.get('window').width;
  const screenHeight = Dimensions.get('window').height;
  
  // 툴팁 너비 계산 (화면 크기에 따라 조정)
  const tooltipWidth = Math.min(300, screenWidth - 40); // 최대 300px, 화면 가로폭의 40px 여백 확보
  
  // 애니메이션 동작 함수
  const animateIn = () => {
    console.log("툴팁 애니메이션 시작");
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 280,
        useNativeDriver: false, // 위치 애니메이션 때문에 false로 설정
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 280,
        useNativeDriver: false, // 위치 애니메이션 때문에 false로 설정
      })
    ]).start(() => {
      console.log("툴팁 애니메이션 완료");
    });
  };
  
  const animateOut = (callback: () => void) => {
    setIsClosing(true);
    console.log("툴팁 닫기 애니메이션 시작");
    
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
      console.log("툴팁 닫기 애니메이션 완료");
    });
  };
  
  // 툴팁이 표시될 때 애니메이션 시작
  useEffect(() => {
    console.log("툴팁 가시성 변경:", isVisible);
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
  
  if (!isVisible && !isClosing) return null;
  
  // 툴팁 위치 계산 로직
  const { top, left, width } = position;
  
  // 툴팁 높이 대략적인 설정
  const tooltipHeight = 120; // 대략적인 높이 설정
  
  // 아이콘 중앙 위치 (화살표의 기준점)
  const iconCenterX = left;
  
  // 화면 경계에 따른 배치 방식 결정
  let arrowPlacement = 'center'; // 기본값
  if (iconCenterX < tooltipWidth / 2 + 40) {
    arrowPlacement = 'left'; // 왼쪽 가장자리에 가까울 때
  } else if (iconCenterX > screenWidth - tooltipWidth / 2 - 40) {
    arrowPlacement = 'right'; // 오른쪽 가장자리에 가까울 때
  }
  
  // 배치 방식에 따라 툴팁과 화살표 위치 조정
  let tooltipLeft;
  let arrowHorizontalPosition;
  
  switch (arrowPlacement) {
    case 'left':
      tooltipLeft = 20; // 왼쪽 여백
      arrowHorizontalPosition = iconCenterX - 7; // 화살표 중앙 위치 조정
      break;
    case 'right':
      tooltipLeft = screenWidth - tooltipWidth - 20; // 오른쪽 여백
      arrowHorizontalPosition = iconCenterX - 7; // 화살표 중앙 위치 조정
      break;
    default: // 'center'
      tooltipLeft = Math.max(20, Math.min(iconCenterX - (tooltipWidth / 2), screenWidth - tooltipWidth - 20));
      arrowHorizontalPosition = iconCenterX - 7; // 화살표 중앙 위치 조정
  }
  
  // 화살표를 툴팁 내부 범위로 제한
  const arrowMin = tooltipLeft + 20; // 툴팁 왼쪽 경계 + 여백
  const arrowMax = tooltipLeft + tooltipWidth - 20; // 툴팁 오른쪽 경계 - 여백
  
  arrowHorizontalPosition = Math.max(arrowMin, Math.min(arrowHorizontalPosition, arrowMax));
  
  // 툴팁 상단 위치 계산
  let tooltipTop = top + 14; // 화살표 아래에 위치 (14px은 화살표 높이)
  
  // 툴팁이 화면 하단을 벗어나는지 확인하고 위치 조정
  if (tooltipTop + tooltipHeight > screenHeight - 50) {
    // 위로 표시 (아이콘 위에)
    tooltipTop = Math.max(50, top - tooltipHeight - 14);
  }
  
  // 툴팁 위치 조정 (화면 경계를 벗어나지 않도록)
  const tooltipStyle = {
    top: tooltipTop,
    left: tooltipLeft,
    width: tooltipWidth,
    opacity: fadeAnim,
    transform: [
      { 
        translateY: fadeAnim.interpolate({
          inputRange: [0, 1],
          outputRange: [5, 0],
        }) 
      },
      { scale: scaleAnim }
    ],
  };
  
  // 툴팁 화살표 위치 조정
  const arrowStyle = {
    top: top, 
    left: arrowHorizontalPosition,
    opacity: fadeAnim,
    transform: [
      { rotate: '45deg' },
      { scale: scaleAnim },
      { 
        translateY: fadeAnim.interpolate({
          inputRange: [0, 1],
          outputRange: [0, 0],
        }) 
      }
    ],
  };

  console.log('툴팁 렌더링:', { 
    top, 
    left, 
    width, 
    tooltipTop: tooltipStyle.top, 
    tooltipLeft: tooltipStyle.left,
    arrowLeft: arrowStyle.left,
    screenWidth,
    screenHeight,
    arrowPlacement,
    isVisible
  });
  
  return (
    <View style={styles.overlay}>
      <TouchableWithoutFeedback onPress={handleClose}>
        <View style={styles.touchableArea}>
          <TooltipArrow style={arrowStyle} color={color} />
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