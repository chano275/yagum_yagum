// src/context/DimensionContext.tsx
import React, { createContext, useContext } from 'react';
import { useWindowDimensions } from 'react-native';

// 모바일 기준 너비 설정
const BASE_MOBILE_WIDTH = 390;
const MAX_MOBILE_WIDTH = 430;

// 컨텍스트 인터페이스 정의
interface DimensionContextType {
  width: number;
  height: number;
}

// 컨텍스트 생성
const DimensionContext = createContext<DimensionContextType>({
  width: 0,
  height: 0,
});

// 프로바이더 컴포넌트
export const DimensionProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { width, height } = useWindowDimensions();

  return (
    <DimensionContext.Provider value={{ width, height }}>
      {children}
    </DimensionContext.Provider>
  );
};

// 커스텀 훅
export const useDimension = () => useContext(DimensionContext);
