// src/components/common/TextComponents.tsx
import styled from "styled-components/native";

// 스타일드 컴포넌트 인터페이스
interface StyledProps {
  width: number;
}

// 공통 제목 텍스트
export const Title = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.056}px;
  color: ${({ theme }) => theme.colors.text};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;

// 서브 제목 텍스트
export const SubTitle = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.04}px;
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.medium};
`;

// 일반 텍스트
export const BodyText = styled.Text<StyledProps>`
  font-size: ${({ width }) => width * 0.035}px;
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.regular};
`;

// 강조 텍스트
export const HighlightText = styled.Text`
  color: ${({ theme }) => theme.colors.primary};
  font-weight: bold;
  font-family: ${({ theme }) => theme.fonts.bold};
`;
