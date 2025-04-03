import React, { createContext, useContext, useState, useEffect } from 'react';
import { teamColors } from '../styles/teamColors';

// DB에 저장될 데이터 타입
interface JoinDataForDB {
  teamId: number;              // TEAM_ID (int)
  favoritePlayerId: number;    // FAVORITE_PLAYER_ID (int)
  savingGoal: number;         // SAVING_GOAL (int)
  dailyLimit: number;         // DAILY_LIMIT (int)
  monthLimit: number;         // MONTH_LIMIT (int)
  sourceAccount: string;      // SOURCE_ACCOUNT (varchar)
}

// UI용 데이터 타입
interface UITeam {
  id: number;  // DB의 TEAM_ID와 매칭
  name: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
  };
  logo: string;
}

interface UIPlayer {
  id: number;  // DB의 FAVORITE_PLAYER_ID와 매칭
  name: string;
  number: string;
  position: string;
  teamId: number;
}

// Context에서 관리할 전체 데이터
interface JoinData {
  // UI 표시용 데이터
  selectedTeam: UITeam | null;
  selectedPlayer: UIPlayer | null;
  
  // 적금 설정
  savingGoal: number | null;
  dailyLimit: number | null;
  monthLimit: number | null;
  sourceAccount: string | null;
}

interface JoinContextType {
  joinData: JoinData;
  // 각 단계별 업데이트 함수
  updateTeam: (team: UITeam) => void;
  updatePlayer: (player: UIPlayer) => void;
  updateSavingGoal: (goal: number) => void;
  updateLimits: (daily: number, monthly: number) => void;
  updateSourceAccount: (account: string) => void;
  clearJoinData: () => void;
  // 최종 제출 시 DB 데이터 반환
  getDBData: () => JoinDataForDB | null;
}

// Context 생성
const JoinContext = createContext<JoinContextType | null>(null);

// Provider 컴포넌트
export const JoinProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 초기 상태 설정 (sessionStorage 체크)
  const [joinData, setJoinData] = useState<JoinData>(() => {
    const savedData = sessionStorage.getItem('joinProgress');
    return savedData ? JSON.parse(savedData) : {
      selectedTeam: null,
      selectedPlayer: null,
      savingGoal: null,
      dailyLimit: null,
      monthLimit: null,
      sourceAccount: null
    };
  });

  // 데이터 변경시 sessionStorage 업데이트
  useEffect(() => {
    sessionStorage.setItem('joinProgress', JSON.stringify(joinData));
  }, [joinData]);

  // 팀 선택 업데이트
  const updateTeam = (team: UITeam) => {
    setJoinData(prev => ({
      ...prev,
      selectedTeam: team,
      // 팀이 변경되면 선수 선택 초기화
      selectedPlayer: null
    }));
  };

  // 선수 선택 업데이트
  const updatePlayer = (player: UIPlayer) => {
    setJoinData(prev => ({
      ...prev,
      selectedPlayer: player
    }));
  };

  // 적금 목표 업데이트
  const updateSavingGoal = (goal: number) => {
    setJoinData(prev => ({
      ...prev,
      savingGoal: goal
    }));
  };

  // 적금 한도 업데이트
  const updateLimits = (daily: number, monthly: number) => {
    setJoinData(prev => ({
      ...prev,
      dailyLimit: daily,
      monthLimit: monthly
    }));
  };

  // 출금 계좌 업데이트
  const updateSourceAccount = (account: string) => {
    setJoinData(prev => ({
      ...prev,
      sourceAccount: account
    }));
  };

  // 데이터 초기화
  const clearJoinData = () => {
    setJoinData({
      selectedTeam: null,
      selectedPlayer: null,
      savingGoal: null,
      dailyLimit: null,
      monthLimit: null,
      sourceAccount: null
    });
    sessionStorage.removeItem('joinProgress');
  };

  // DB 형식으로 데이터 변환
  const getDBData = (): JoinDataForDB | null => {
    const { selectedTeam, selectedPlayer, savingGoal, dailyLimit, monthLimit, sourceAccount } = joinData;
    
    if (!selectedTeam || !selectedPlayer || !savingGoal || 
        !dailyLimit || !monthLimit || !sourceAccount) {
      return null;
    }

    return {
      teamId: selectedTeam.id,
      favoritePlayerId: selectedPlayer.id,
      savingGoal,
      dailyLimit,
      monthLimit,
      sourceAccount
    };
  };

  return (
    <JoinContext.Provider value={{
      joinData,
      updateTeam,
      updatePlayer,
      updateSavingGoal,
      updateLimits,
      updateSourceAccount,
      clearJoinData,
      getDBData
    }}>
      {children}
    </JoinContext.Provider>
  );
};

// Context 사용을 위한 Hook
export const useJoin = () => {
  const context = useContext(JoinContext);
  if (!context) {
    throw new Error('useJoin must be used within a JoinProvider');
  }
  return context;
}; 