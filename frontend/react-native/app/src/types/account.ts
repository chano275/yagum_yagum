export interface SavingsAccount {
  account_id: string;
  account_num: string;
  total_amount: number;
  interest_rate: number;
  saving_goal: number;
  progress_percentage: number;
  team_name: string | null;
  created_at: string;
}

export interface SourceAccount {
  account_num: string;
  total_amount: number;
}

export interface UserAccountsResponse {
  user_id: string;
  user_email: string;
  user_name: string;
  source_account: SourceAccount;
  savings_accounts: SavingsAccount[];
}

export interface TransactionHistory {
  transactionId: string;
  transactionDate: string;
  transactionType: string;
  summary: string;
  balance: string;
  afterBalance: string;
} 