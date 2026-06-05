import api from './api';

export interface DashboardStats {
  words_learned: number;
  hours_learned: number;
  streak_days: number;
  sentences_practiced: number;
}

export const statsService = {
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/stats/dashboard');
    return response.data;
  },
};

export default statsService;