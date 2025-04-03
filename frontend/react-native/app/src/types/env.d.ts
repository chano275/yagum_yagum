declare module '@env' {
  export const REACT_APP_API_URL: string;
  export const REACT_APP_LOCAL_URL: string;
}

// 전역 NodeJS 타입에 환경변수 추가
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test';
      REACT_APP_API_URL: string;
      REACT_APP_LOCAL_URL: string;
    }
  }
} 