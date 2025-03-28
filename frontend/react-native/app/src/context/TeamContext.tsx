// src/context/TeamContext.tsx
import React, { createContext, useContext, useState } from 'react';

interface TeamColor {
  primary: string;
  secondary: string;
}

interface TeamContextType {
  teamColor: TeamColor;
  setTeamColor: (color: TeamColor) => void;
}

const TeamContext = createContext<TeamContextType>({
  teamColor: {
    primary: '#2D5BFF',
    secondary: '#F0F2FF',
  },
  setTeamColor: () => {},
});

export const useTeam = () => useContext(TeamContext);

export const TeamProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [teamColor, setTeamColor] = useState<TeamColor>({
    primary: '#2D5BFF',
    secondary: '#F0F2FF',
  });

  return (
    <TeamContext.Provider value={{ teamColor, setTeamColor }}>
      {children}
    </TeamContext.Provider>
  );
};
