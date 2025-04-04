import axios from "axios";
import AsyncStorage from '@react-native-async-storage/async-storage';
import { REACT_APP_API_URL, REACT_APP_LOCAL_URL } from "@env";

// const BASE_URL = 'http://localhost:8000';  // 개발 환경

// 배포 환경용
const BASE_URL = 'http://3.38.183.156:8000';  // 배포 환경

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// 요청 인터셉터
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    } catch (error) {
      console.error('토큰 가져오기 실패:', error);
      return config;
    }
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await AsyncStorage.removeItem("token");
        await AsyncStorage.removeItem("user");
        // React Native에서는 window.location.href 대신 navigation을 사용해야 함
        // 여기서는 401 에러만 처리하고, 실제 네비게이션은 컴포넌트에서 처리
      } catch (storageError) {
        console.error('토큰 삭제 실패:', storageError);
      }
    }
    return Promise.reject(error);
  }
);
