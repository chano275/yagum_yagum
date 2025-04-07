import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { teamColors } from '../styles/teamColors';

// DB에 저장될 데이터 타입
interface JoinDataForDB {
  TEAM_ID: number;              
  FAVORITE_PLAYER_ID: number;    
  SAVING_GOAL: number;         
  DAILY_LIMIT: number;         
  MONTH_LIMIT: number;         
  SOURCE_ACCOUNT: string;      
  saving_rules: Array<{
    SAVING_RULE_DETAIL_ID: number;
    SAVING_RULED_AMOUNT: number;
  }>;
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

  // 추가: 규칙 설정 데이터
  savingRules?: {
    win: {
      enabled: boolean;
      amount: number;
    };
    basic: {
      enabled: boolean;
      hit: number;
      homerun: number;
      score: number;
      doublePlay: number;
      error: number;
      sweep: number;
    };
    pitcher: {
      enabled: boolean;
      strikeout: number;
      walk: number;
      run: number;
    };
    batter: {
      enabled: boolean;
      hit: number;
      homerun: number;
      steal: number;
    };
    opponent: {
      enabled: boolean;
      hit: number;
      homerun: number;
      doublePlay: number;
      error: number;
    };
  };

  // 추가: 백엔드로 전송할 형태의 규칙 데이터
  savingRulesForAPI?: Array<{
    SAVING_RULE_DETAIL_ID: number;
    SAVING_RULED_AMOUNT: number;
  }>;
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
  // 규칙 설정 업데이트
  updateSavingRules: (rules: JoinData['savingRules']) => void;
  // 규칙 ID 매핑 적용 함수 추가
  applyRuleIdMapping: () => void;
  // 서버에서 매핑된 규칙 정보 업데이트 함수 추가
  updateSavingRulesForAPI: (rules: Array<{SAVING_RULE_DETAIL_ID: number; SAVING_RULED_AMOUNT: number}>) => void;
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
      sourceAccount: null,
      // 기본 규칙 설정
      savingRules: {
        win: {
          enabled: true,
          amount: 5000,
        },
        basic: {
          enabled: true,
          hit: 500,
          homerun: 1000,
          score: 500,
          doublePlay: 500,
          error: 500,
          sweep: 2000,
        },
        pitcher: {
          enabled: false,
          strikeout: 1000,
          walk: 500,
          run: 1000,
        },
        batter: {
          enabled: false,
          hit: 1000,
          homerun: 5000,
          steal: 2000,
        },
        opponent: {
          enabled: false,
          hit: 500,
          homerun: 1000,
          doublePlay: 1000,
          error: 1000,
        },
      },
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
  
  // 규칙 설정 업데이트
  const updateSavingRules = (rules: JoinData['savingRules']) => {
    setJoinData(prev => ({
      ...prev,
      savingRules: rules
    }));
  };

  // 규칙 ID 매핑 적용 함수
  const applyRuleIdMapping = () => {
    if (!joinData.savingRules) return;
    
    // 이미 매핑된 규칙들이 있다면 그대로 사용
    if (joinData.savingRulesForAPI && joinData.savingRulesForAPI.length > 0) {
      console.log('이미 매핑된 규칙 정보 사용:', joinData.savingRulesForAPI);
      return;
    }
    
    // 이미 매핑된 규칙이 없는 경우 새로 매핑 진행
    const { savingRules } = joinData;
    const savingRulesForAPI: Array<{
      SAVING_RULE_DETAIL_ID: number;
      SAVING_RULED_AMOUNT: number;
    }> = [];
    
    // 승리 규칙 추가
    if (savingRules.win.enabled && savingRules.win.amount > 0) {
      savingRulesForAPI.push({
        SAVING_RULE_DETAIL_ID: 1, // 승리 규칙의 ID
        SAVING_RULED_AMOUNT: savingRules.win.amount
      });
    }
    
    // 기본 규칙 추가 (팀 기록)
    if (savingRules.basic?.enabled) {
      // 안타
      if (savingRules.basic.hit > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 2, // 팀 안타 규칙의 ID
          SAVING_RULED_AMOUNT: savingRules.basic.hit
        });
      }
      
      // 홈런
      if (savingRules.basic.homerun > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 3, // 팀 홈런 규칙의 ID
          SAVING_RULED_AMOUNT: savingRules.basic.homerun
        });
      }
      
      // 득점
      if (savingRules.basic.score > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 4, // 팀 득점 규칙의 ID
          SAVING_RULED_AMOUNT: savingRules.basic.score
        });
      }
      
      // 병살타
      if (savingRules.basic.doublePlay > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 5, // 팀 병살타 규칙의 ID
          SAVING_RULED_AMOUNT: savingRules.basic.doublePlay
        });
      }
      
      // 실책
      if (savingRules.basic.error > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 6, // 팀 실책 규칙의 ID
          SAVING_RULED_AMOUNT: savingRules.basic.error
        });
      }
      
      // 스윕
      if (savingRules.basic.sweep > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 7, // 팀 스윕 규칙의 ID
          SAVING_RULED_AMOUNT: savingRules.basic.sweep
        });
      }
    }
    
    // 투수 규칙 추가
    if (savingRules.pitcher.enabled) {
      // 삼진
      if (savingRules.pitcher.strikeout > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 8, // 투수 삼진 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.pitcher.strikeout
        });
      }
      
      // 볼넷
      if (savingRules.pitcher.walk > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 9, // 투수 볼넷 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.pitcher.walk
        });
      }
      
      // 자책
      if (savingRules.pitcher.run > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 10, // 투수 자책 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.pitcher.run
        });
      }
    }
    
    // 타자 규칙 추가
    if (savingRules.batter.enabled) {
      // 안타
      if (savingRules.batter.hit > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 11, // 타자 안타 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.batter.hit
        });
      }
      
      // 홈런
      if (savingRules.batter.homerun > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 12, // 타자 홈런 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.batter.homerun
        });
      }
      
      // 도루
      if (savingRules.batter.steal > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 13, // 타자 도루 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.batter.steal
        });
      }
    }
    
    // 상대팀 규칙 추가
    if (savingRules.opponent.enabled) {
      // 안타
      if (savingRules.opponent.hit > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 14, // 상대팀 안타 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.opponent.hit
        });
      }
      
      // 홈런
      if (savingRules.opponent.homerun > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 15, // 상대팀 홈런 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.opponent.homerun
        });
      }
      
      // 병살타
      if (savingRules.opponent.doublePlay > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 16, // 상대팀 병살타 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.opponent.doublePlay
        });
      }
      
      // 실책
      if (savingRules.opponent.error > 0) {
        savingRulesForAPI.push({
          SAVING_RULE_DETAIL_ID: 17, // 상대팀 실책 규칙 ID
          SAVING_RULED_AMOUNT: savingRules.opponent.error
        });
      }
    }
    
    // 상태 업데이트
    setJoinData(prev => ({
      ...prev,
      savingRulesForAPI
    }));
    
    console.log('새로 매핑된 규칙 정보:', savingRulesForAPI);
  };

  // 데이터 초기화
  const clearJoinData = () => {
    setJoinData({
      selectedTeam: null,
      selectedPlayer: null,
      savingGoal: null,
      dailyLimit: null,
      monthLimit: null,
      sourceAccount: null,
      // 기본 규칙 설정 유지
      savingRules: {
        win: {
          enabled: true,
          amount: 5000,
        },
        basic: {
          enabled: true,
          hit: 500,
          homerun: 1000,
          score: 500,
          doublePlay: 500,
          error: 500,
          sweep: 2000,
        },
        pitcher: {
          enabled: false,
          strikeout: 1000,
          walk: 500,
          run: 1000,
        },
        batter: {
          enabled: false,
          hit: 1000,
          homerun: 5000,
          steal: 2000,
        },
        opponent: {
          enabled: false,
          hit: 500,
          homerun: 1000,
          doublePlay: 1000,
          error: 1000,
        },
      },
    });
    sessionStorage.removeItem('joinProgress');
  };

  // DB 형식으로 데이터 변환
  const getDBData = (): JoinDataForDB | null => {
    const { selectedTeam, selectedPlayer, savingGoal, dailyLimit, monthLimit, sourceAccount, savingRulesForAPI } = joinData;
    
    if (!selectedTeam || !selectedPlayer || !savingGoal || 
        !dailyLimit || !monthLimit || !sourceAccount) {
      return null;
    }

    return {
      TEAM_ID: selectedTeam.id,
      FAVORITE_PLAYER_ID: selectedPlayer.id,
      SAVING_GOAL: savingGoal,
      DAILY_LIMIT: dailyLimit,
      MONTH_LIMIT: monthLimit,
      SOURCE_ACCOUNT: sourceAccount,
      saving_rules: savingRulesForAPI || []
    };
  };

  // 서버에서 매핑된 규칙 정보 업데이트 함수
  const updateSavingRulesForAPI = (rules: Array<{SAVING_RULE_DETAIL_ID: number; SAVING_RULED_AMOUNT: number}>) => {
    setJoinData(prev => ({
      ...prev,
      savingRulesForAPI: rules
    }));
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
      getDBData,
      updateSavingRules,
      applyRuleIdMapping,
      updateSavingRulesForAPI
    }}>
      {children}
    </JoinContext.Provider>
  );
};

// useJoin 훅 추가
export const useJoin = () => {
  const context = useContext(JoinContext);
  if (!context) {
    throw new Error('useJoin must be used within a JoinProvider');
  }
  return context;
}; 