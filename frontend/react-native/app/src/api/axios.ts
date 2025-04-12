import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { REACT_APP_API_URL, REACT_APP_LOCAL_URL } from "@env";

// const BASE_URL = "http://localhost:8000"; // 개발 환경

// 배포 환경용
// const BASE_URL = 'http://3.38.183.156:8000';  // 배포 환경
const BASE_URL = 'https://j12b206.p.ssafy.io/backend';  // 배포 환경

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    Accept: "application/json",
  },
});

api.interceptors.request.use(
  async (config) => {
    // FormData인 경우 Content-Type을 명시적으로 삭제하는 로직을 추가할 수도 있지만,
    // 기본값을 제거했으므로 Axios가 자동으로 처리할 가능성이 높습니다.
    // 일단 기본값 제거만으로 테스트해보세요.
    // if (config.data instanceof FormData) {
    //   delete config.headers['Content-Type'];
    // }
    try {
      const token = await AsyncStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    } catch (error) {
      console.error("토큰 가져오기 실패:", error);
      return config;
    }
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await AsyncStorage.removeItem("token");
        await AsyncStorage.removeItem("user");
      } catch (storageError) {
        console.error("토큰 삭제 실패:", storageError);
      }
    }
    return Promise.reject(error);
  }
);
