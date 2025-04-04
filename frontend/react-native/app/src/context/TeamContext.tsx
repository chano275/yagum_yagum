// src/context/TeamContext.tsx
import React, { createContext, useState, useContext } from "react";
import {
  teamColors,
  defaultTeam,
  teamIdToCode,
  teamNameToCode,
} from "../styles/teamColors";

type TeamType = {
  team_id: number;
  team_name: string;
  team_color: string;
  team_color_secondary?: string;
  team_color_background?: string;
};

interface TeamData {
  team_id: number;
  team_name: string;
  account_id: number;
}

export type TeamContextType = {
  currentTeam: TeamType | undefined;
  teamName: string | undefined;
  teamId: number;
  teamColor: {
    primary: string;
    secondary: string;
    background: string;
  };
  setTeamData: (team: TeamType) => void;
};

const TeamContext = createContext<TeamContextType | undefined>(undefined);

export const TeamProvider = ({ children }: { children: React.ReactNode }) => {
  const [currentTeam, setCurrentTeam] = useState<TeamType>();
  const [teamName, setTeamName] = useState<string>();
  const [teamId, setTeamId] = useState<number>(0);
  const [teamColor, setTeamColor] = useState({
    primary: '#000000',
    secondary: '#FFFFFF',
    background: '#FFFFFF',
  });

  const setTeamData = (team: TeamType) => {
    setCurrentTeam(team);
    setTeamName(team.team_name);
    setTeamId(team.team_id);
    setTeamColor({
      primary: team.team_color,
      secondary: team.team_color_secondary || '#FFFFFF',
      background: team.team_color_background || '#FFFFFF',
    });
  };

  return (
    <TeamContext.Provider
      value={{
        currentTeam,
        teamName,
        teamId,
        teamColor,
        setTeamData,
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
