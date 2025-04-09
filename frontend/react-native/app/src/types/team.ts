export interface Player {
  PLAYER_ID: number;
  PLAYER_NAME: string;
  PLAYER_NUM: string;
  PLAYER_TYPE_ID: number;
  player_type_name: string;
  PLAYER_IMAGE_URL: string;
}

export interface TeamFullDetail {
  TEAM_ID: number;
  TEAM_NAME: string;
  TOTAL_WIN: number;
  TOTAL_LOSE: number;
  TOTAL_DRAW: number;
  created_at: string;
  win_rate: number;
  total_games: number;
  players: Player[];
  accounts: any[];
  upcoming_games: any[];
} 