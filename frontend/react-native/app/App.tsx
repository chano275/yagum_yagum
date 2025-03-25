import { StatusBar } from "expo-status-bar";
import { ThemeProvider } from "styled-components/native";
import styled from "styled-components/native";
import { theme } from "./src/styles/theme";
import { useFonts } from "expo-font";

// 스타일 컴포넌트 정의
const Container = styled.View`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  justify-content: center;
  align-items: center;
`;

const Title = styled.Text`
  font-size: ${({ theme }) => theme.fontSize.xxl};
  color: ${({ theme }) => theme.colors.text};
  font-weight: bold;
  font-family: "Pretendard-Bold";
`;

const StyledButton = styled.TouchableOpacity`
  background-color: ${({ theme }) => theme.colors.primary};
  padding: ${({ theme }) => theme.spacing.md};
  border-radius: 8px;
  margin-top: ${({ theme }) => theme.spacing.lg};
`;

const ButtonText = styled.Text`
  color: white;
  font-size: ${({ theme }) => theme.fontSize.md};
  font-family: "Pretendard-Regular";
`;

export default function App() {
  const [fontsLoaded] = useFonts({
    "Pretendard-Bold": require("./assets/fonts/Pretendard-Bold.otf"),
    "Pretendard-Light": require("./assets/fonts/Pretendard-Light.otf"),
    "Pretendard-Medium": require("./assets/fonts/Pretendard-Medium.otf"),
    "Pretendard-Regular": require("./assets/fonts/Pretendard-Regular.otf"),
  });

  if (!fontsLoaded) {
    return null; // 폰트가 로드되지 않았을 때 빈 화면 표시
  }

  return (
    <ThemeProvider theme={theme}>
      <Container>
        <StatusBar style="auto" />
        <Title>리액트 네이티브 시작하기</Title>
        <StyledButton>
          <ButtonText>시작하기</ButtonText>
        </StyledButton>
      </Container>
    </ThemeProvider>
  );
}
