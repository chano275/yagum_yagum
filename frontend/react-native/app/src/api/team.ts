import { api } from './axios';
import { TeamFullDetail, GameResultResponse } from '../types/team';

export const getTeamFullDetails = async (teamId: number): Promise<TeamFullDetail> => {
  const response = await api.get(`/api/teams/${teamId}/details`);
  return response.data;
};

export const getUserTeamGameResults = async (endDate?: string): Promise<GameResultResponse[]> => {
  try {
    const params: { end_date?: string } = {};
    if (endDate) {
      params.end_date = endDate;
    }

    const response = await api.get('/api/team/game_results', { params });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch game results:', error);
    throw error;
  }
}; 