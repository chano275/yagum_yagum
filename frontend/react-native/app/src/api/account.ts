import { api } from './axios';
import { UserAccountsResponse, TransactionHistory } from '../types/account';
import axios from 'axios';

export const getUserAccounts = async (): Promise<UserAccountsResponse> => {
  try {
    console.log('API Request URL:', `${api.defaults.baseURL}/api/user/accounts`);
    const response = await api.get<UserAccountsResponse>('/api/user/accounts');
    return response.data;
  } catch (error) {
    console.error('계좌 정보 조회 실패:', error);
    if (axios.isAxiosError(error)) {
      console.error('상세 에러 정보:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
      });
    }
    throw error;
  }
};

export const getTransactionHistory = async (): Promise<TransactionHistory[]> => {
  try {
    const response = await api.get<TransactionHistory[]>('/api/user/transaction-history');
    return response.data;
  } catch (error) {
    console.error('거래 내역 조회 실패:', error);
    if (axios.isAxiosError(error)) {
      console.error('상세 에러 정보:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
      });
    }
    throw error;
  }
}; 