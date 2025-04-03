// src/context/TeamContext.tsx
import React, { createContext, useState, useContext } from "react";
import {
  teamColors,
  defaultTeam,
  teamIdToCode,
  teamNameToCode,
} from "../styles/teamColors";

type TeamType = keyof typeof teamColors;

interface TeamData {
  team_id: number;
  team_name: string;
  account_id: number;
}

interface TeamContextType {
  currentTeam: TeamType;
  teamName: string | undefined;
  setCurrentTeam: (team: TeamType) => void;
  setTeamById: (id: number) => void;
  setTeamByName: (name: string) => void;
  setTeamData: (data: TeamData) => void;
  teamColor: {
    primary: string;
    secondary: string;
    background: string;
  };
}

const TeamContext = createContext<TeamContextType | undefined>(undefined);

export const TeamProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [currentTeam, setCurrentTeam] = useState<TeamType>(defaultTeam);
  const [teamName, setTeamName] = useState<string | undefined>(undefined);

  // 팀 ID로 팀 설정
  const setTeamById = (id: number) => {
    const teamCode = teamIdToCode[id];
    if (teamCode) {
      setCurrentTeam(teamCode);
    }
  };

  // 팀 이름으로 팀 설정
  const setTeamByName = (name: string) => {
    setTeamName(name);
    const teamCode = teamNameToCode[name];
    if (teamCode) {
      setCurrentTeam(teamCode);
    }
  };

  // API 응답에서 팀 데이터 설정
  const setTeamData = (data: TeamData) => {
    if (data && data.team_id) {
      setTeamById(data.team_id);
      setTeamName(data.team_name);
    }
  };

  // 현재 팀 색상 가져오기
  const teamColor = teamColors[currentTeam] || teamColors[defaultTeam];

  return (
    <TeamContext.Provider
      value={{
        currentTeam,
        teamName,
        setCurrentTeam,
        setTeamById,
        setTeamByName,
        setTeamData,
        teamColor,
      }}
    >
      {children}
    </TeamContext.Provider>
  );
};

// 커스텀 훅으로 쉽게 사용
export const useTeam = () => {
  const context = useContext(TeamContext);
  if (!context) {
    throw new Error("useTeam must be used within a TeamProvider");
  }
  return context;
};
