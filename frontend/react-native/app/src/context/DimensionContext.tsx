// src/context/DimensionContext.tsx
import React, { createContext, useContext } from "react";
import { useWindowDimensions, Platform } from "react-native";

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// 컨텍스트 인터페이스 정의
interface DimensionContextType {
  width: number;
  BASE_MOBILE_WIDTH: number;
  MAX_MOBILE_WIDTH: number;
}

// 컨텍스트 생성
const DimensionContext = createContext<DimensionContextType | undefined>(
  undefined
);

// 프로바이더 컴포넌트
export const DimensionProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { width: windowWidth } = useWindowDimensions();

  // 웹과 모바일 환경에 따른 너비 계산 (한 번만 수행)
  const width =
    Platform.OS === "web"
      ? BASE_MOBILE_WIDTH
      : Math.min(windowWidth, MAX_MOBILE_WIDTH);

  return (
    <DimensionContext.Provider
      value={{ width, BASE_MOBILE_WIDTH, MAX_MOBILE_WIDTH }}
    >
      {children}
    </DimensionContext.Provider>
  );
};

// 커스텀 훅
export const useDimension = () => {
  const context = useContext(DimensionContext);
  if (!context) {
    throw new Error("useDimension must be used within a DimensionProvider");
  }
  return context;
};
