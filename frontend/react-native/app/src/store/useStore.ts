import { create } from 'zustand';
import { UserAccountsResponse } from '../types/account';
import { getUserAccounts } from '../api/account';

export interface AuthState {
  isLoggedIn: boolean;
  token: string | null;
  user: { id: string; name: string } | null;
  setAuth: (token: string, user: { id: string; name: string }) => void;
  logout: () => void;
}

export const useStore = create<AuthState>((set) => ({
  isLoggedIn: false,
token: null,
user: null,
  setAuth: (token: string, user: { id: string; name: string }) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ isLoggedIn: true, token, user });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ isLoggedIn: false, token: null, user: null });
  }
}));

interface AccountStore {
  accountInfo: UserAccountsResponse | null;
  isLoading: boolean;
  error: string | null;
  fetchAccountInfo: () => Promise<void>;
}

export const useAccountStore = create<AccountStore>((set) => ({
  accountInfo: null,
  isLoading: false,
  error: null,
  fetchAccountInfo: async () => {
    try {
      set({ isLoading: true, error: null });
      const data = await getUserAccounts();
      set({ accountInfo: data });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '계좌 정보를 가져오는데 실패했습니다.' });
    } finally {
      set({ isLoading: false });
    }
  },
}));