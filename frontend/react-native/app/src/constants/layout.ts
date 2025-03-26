import { Platform } from 'react-native';
import styled from 'styled-components/native';

// 기본 너비 상수
export const BASE_MOBILE_WIDTH = 390;  // iPhone 13 기준
export const MAX_MOBILE_WIDTH = 428;   // 큰 폰 기준 최대 너비

// 스타일드 컴포넌트용 인터페이스
export interface StyledProps {
  width: number;
}

// 공통 래퍼 컴포넌트
export const AppWrapper = styled.View`flex:1;align-items:center;background-color:#FFFFFF;width:100%`;

export const MobileContainer = styled.View<StyledProps>`width:${({ width }) => {
    const isWeb = Platform.OS === 'web';
    const deviceWidth = Math.min(width, MAX_MOBILE_WIDTH);
    return isWeb ? `${BASE_MOBILE_WIDTH}px` : `${deviceWidth}px`;
  }};max-width:100%;flex:1;align-self:center;overflow:hidden;position:relative;${Platform.OS === 'web' && `box-shadow:0px 0px 10px rgba(0, 0, 0, 0.1);margin:0 auto;`}`;

// 너비 계산 유틸리티 함수
export const getAdjustedWidth = (windowWidth: number) => {
  return Platform.OS === 'web' ? 
    BASE_MOBILE_WIDTH : 
    Math.min(windowWidth, MAX_MOBILE_WIDTH);
}; 