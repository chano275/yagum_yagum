import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Platform } from 'react-native';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

interface CountState {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export interface AppState extends AuthState, CountState {}

// 웹 환경과 모바일 환경에 따라 다른 스토리지 사용
const storage = Platform.select({
  web: createJSONStorage(() => localStorage),
  default: createJSONStorage(() => {
    return {
      getItem: (key: string) => {
        const item = localStorage.getItem(key);
        return item ? Promise.resolve(item) : Promise.resolve(null);
      },
      setItem: (key: string, value: string) => {
        localStorage.setItem(key, value);
        return Promise.resolve();
      },
      removeItem: (key: string) => {
        localStorage.removeItem(key);
        return Promise.resolve();
      },
    };
  }),
});

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Auth state
      token: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),

      // Count state
      count: 0,
      increment: () => set((state) => ({ count: state.count + 1 })),
      decrement: () => set((state) => ({ count: state.count - 1 })),
      reset: () => set({ count: 0 })
    }),
    {
      name: 'app-storage',
      storage,
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);