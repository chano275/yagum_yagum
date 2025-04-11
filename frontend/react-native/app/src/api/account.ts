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

interface CheckAccountResponse {
  NAME: string;
  ACCOUNT_NUM: string;
  BOOL: boolean;
}

export const checkAccountNumber = async (accountNum: string): Promise<CheckAccountResponse> => {
  const response = await api.get<CheckAccountResponse>(`/api/user/check-account-num?account_num=${accountNum}`);
  return response.data;
};

interface TransferMoneyRequest {
  deposit_account_no: string;
  balance: number;
}

export const transferMoney = async (data: TransferMoneyRequest) => {
  try {
    console.log('이체 요청 데이터:', data);
    const response = await api.post('/api/user/transfer-money', null, {
      params: {
        deposit_account_no: data.deposit_account_no,
        balance: data.balance
      }
    });
    return response.data;
  } catch (error) {
    console.error('이체 요청 실패:', error);
    if (axios.isAxiosError(error)) {
      console.error('상세 에러 정보:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
    }
    throw error;
  }
};

// 월별 거래 내역 조회
export const getMonthlyTransfers = async (month?: number) => {
  try {
    const response = await api.get('/api/account/transfers_log', {
      params: { month }
    });
    return response.data;
  } catch (error) {
    console.error('월별 거래 내역 조회 실패:', error);
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

// 일일 적금 상세 내역 조회
export const getDailySavingDetail = async (date: string) => {
  try {
    console.log("일일 적금 상세 내역 조회 요청:", date);
    const response = await api.get(`/api/account/daily-savings-detail?date=${date}`);
    console.log("일일 적금 상세 내역 응답:", response.data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("일일 적금 상세 내역 조회 실패:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: error.response?.headers,
      });
    }
    throw error;
  }
}; 