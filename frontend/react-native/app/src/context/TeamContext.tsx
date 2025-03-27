// src/context/TeamContext.tsx
import React, { createContext, useState, useContext } from "react";
import { teamColors, defaultTeam } from "../styles/teamColors";

interface TeamContextType {
  currentTeam: string;
  setCurrentTeam: (team: string) => void;
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
  const [currentTeam, setCurrentTeam] = useState(defaultTeam);

  // 현재 팀 색상 가져오기
  const teamColor = teamColors[currentTeam] || teamColors[defaultTeam];

  return (
    <TeamContext.Provider value={{ currentTeam, setCurrentTeam, teamColor }}>
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
