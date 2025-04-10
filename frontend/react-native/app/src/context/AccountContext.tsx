import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAccountStore } from '../store/useStore';

interface AccountContextType {
  balance: string;
  accountNumber: string;
  fetchAccountInfo: () => Promise<void>;
}

const AccountContext = createContext<AccountContextType | null>(null);

export const AccountProvider = ({ children }: { children: React.ReactNode }) => {
  const { accountInfo, fetchAccountInfo } = useAccountStore();
  
  // 컴포넌트 마운트 시 계좌 정보 가져오기
  useEffect(() => {
    fetchAccountInfo();
  }, []);

  const balance = accountInfo?.source_account?.total_amount?.toLocaleString() + '원' || '0원';
  const accountNumber = accountInfo?.source_account?.account_num || 'xxx-xxxx-xxxx';

  return (
    <AccountContext.Provider 
      value={{ 
        balance, 
        accountNumber,
        fetchAccountInfo
      }}
    >
      {children}
    </AccountContext.Provider>
  );
};

export const useAccount = () => {
  const context = useContext(AccountContext);
  if (!context) {
    throw new Error('useAccount must be used within an AccountProvider');
  }
  return context;
}; 