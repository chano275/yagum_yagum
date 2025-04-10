// 앱에서 사용할 공통 타입 정의
export interface User {
    id: string;
    name: string;
    email: string;
  }
  
  export type NavigationParams = {
    Home: undefined;
    Profile: { userId: string };
    Settings: undefined;
  };