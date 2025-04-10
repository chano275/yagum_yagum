export const theme = {
  colors: {
    primary: "#007AFF",
    secondary: "#5856D6",
    background: "#FFFFFF",
    text: "#000000",
    grey: "#8E8E93",
    lightGrey: "#C7C7CC",
  },
  spacing: {
    xs: "4px",
    sm: "8px",
    md: "16px",
    lg: "24px",
    xl: "32px",
  },
  fontSize: {
    xs: "12px",
    sm: "14px",
    md: "16px",
    lg: "18px",
    xl: "20px",
    xxl: "24px",
  },
  fonts: {
    regular: "Pretendard-Regular", // 기본 폰트
    bold: "Pretendard-Bold", // Bold 폰트
    medium: "Pretendard-Medium", // Medium 폰트
    light: "Pretendard-Light", // Light 폰트
  },
};

export type Theme = typeof theme;
