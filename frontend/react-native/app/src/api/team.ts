import { api } from './axios';
import { TeamFullDetail } from '../types/team';

export const getTeamFullDetails = async (teamId: number): Promise<TeamFullDetail> => {
  const response = await api.get(`/api/teams/${teamId}/details`);
  return response.data;
}; 