import { create } from 'zustand';

// 상태 인터페이스 정의
interface AppState {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

// 스토어 생성
export const useAppStore = create<AppState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 })
}));