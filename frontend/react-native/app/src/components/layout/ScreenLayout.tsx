// src/components/layout/ScreenLayout.tsx
import React from "react";
import { SafeAreaView, Platform } from "react-native";
import styled from "styled-components/native";
import { useDimension } from "../../context/DimensionContext";

// 스타일드 컴포넌트 인터페이스
interface StyledProps {
  width: number;
}

// 앱 전체 래퍼 컴포넌트
const AppWrapper = styled.View`
  flex: 1;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.background};
  width: 100%;
`;

// 모바일 컨테이너 (너비 제한)
const MobileContainer = styled.View<StyledProps>`
  width: ${({ width }) => `${width}px`};
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
`;

// 공통 레이아웃 컴포넌트
interface ScreenLayoutProps {
  children: (width: number) => React.ReactNode;
}

const ScreenLayout: React.FC<ScreenLayoutProps> = ({ children }) => {
  // 컨텍스트에서 너비 가져오기 (중복 계산 제거)
  const { width } = useDimension();

  return (
    <AppWrapper>
      <MobileContainer width={width}>
        <SafeAreaView style={{ flex: 1 }}>{children(width)}</SafeAreaView>
      </MobileContainer>
    </AppWrapper>
  );
};

export default ScreenLayout;
