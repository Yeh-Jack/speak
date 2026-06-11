import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface DashboardStats {
  words_learned: number;
  hours_learned: number;
  streak_days: number;
  sentences_practiced: number;
  daily_goal_minutes: number;
  daily_goal_progress: number;
  daily_goal_remaining: number;
  today_minutes: number;
  date: string;
}

export const useStatsStore = defineStore('stats', () => {
  const dashboardStats = ref<DashboardStats | null>(null);
  const isLoading = ref(false);

  function setDashboardStats(stats: DashboardStats) {
    dashboardStats.value = stats;
  }

  function incrementWordsLearned() {
    if (dashboardStats.value) {
      dashboardStats.value.words_learned += 1;
    }
  }

  return {
    dashboardStats,
    isLoading,
    setDashboardStats,
    incrementWordsLearned,
  };
});