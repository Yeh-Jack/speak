<script setup lang="ts">
import { ref, computed, onMounted, onActivated, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useI18n } from '@/composables/useI18n';
import { useLanguageStore } from '@/stores/language.store';
import { videoService, type VideoResponse } from '@/services/video.service';
import { statsService } from '@/services/stats.service';
import { useVideoStore } from '@/stores/video.store';
import type { Video } from '@/types';

const router = useRouter();
const { user } = useAuth();
const videoStore = useVideoStore();
const { t } = useI18n();
const languageStore = useLanguageStore();

const videos = ref<Video[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const showAddModal = ref(false);
const youtubeUrl = ref('');
const chunkDuration = ref(Number(import.meta.env.VITE_DEFAULT_CHUNK_SIZE) || 30);
const youtubeUrlInput = ref<HTMLInputElement | null>(null);

const dashboardStats = ref({
  wordsLearned: 0,
  hoursLearned: 0,
  streakDays: 0,
  sentencesPracticed: 0,
  dailyGoalMinutes: 30,
  dailyGoalProgress: 0,
  dailyGoalRemaining: 30,
  todayMinutes: 0,
});
const statsLoading = ref(true);

const chunkDurationOptions = computed(() => [
  { value: 30, label: t('30 sec', '30秒'), description: t('Quick practice', '快速練習') },
  { value: 60, label: t('1 min', '1分鐘'), description: t('Short segments', '短片段') },
  { value: 180, label: t('3 min', '3分鐘'), description: t('Medium segments', '中片段') },
  { value: 300, label: t('5 min', '5分鐘'), description: t('Standard segments', '標準片段') },
  { value: 600, label: t('10 min', '10分鐘'), description: t('Extended segments', '長片段') },
]);

const stats = computed(() => ({
  wordsLearned: dashboardStats.value.wordsLearned,
  hoursLearned: dashboardStats.value.hoursLearned,
  streakDays: dashboardStats.value.streakDays,
  sentencesPracticed: dashboardStats.value.sentencesPracticed,
  dailyGoalMinutes: dashboardStats.value.dailyGoalMinutes,
  dailyGoalProgress: dashboardStats.value.dailyGoalProgress,
  dailyGoalRemaining: dashboardStats.value.dailyGoalRemaining,
  todayMinutes: dashboardStats.value.todayMinutes,
}));

const recentVideos = computed(() =>
  videos.value.slice(0, 4).map(v => ({
    id: v.id,
    title: v.title,
    duration: formatDuration(v.duration),
    progress: v.status === 'ready' ? 0 : 0,
    thumbnail: v.thumbnail || `https://picsum.photos/seed/${v.id}/320/180`,
    notes: v.study_plan_notes || '',
    notesZh: v.study_plan_notes_zh || '',
  }))
);

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function goToVideo(videoId: string) {
  router.push(`/videos/${videoId}`);
}



function openAddModal() {
  showAddModal.value = true;
  youtubeUrl.value = '';
  videoStore.setCreatingVideo(false);
  nextTick(() => {
    youtubeUrlInput.value?.focus();
  });
}

function closeAddModal() {
  showAddModal.value = false;
  youtubeUrl.value = '';
  chunkDuration.value = 300;
}

async function createVideoFromYouTube() {
  if (!youtubeUrl.value.trim()) {
    videoStore.setCreatingVideo(false, '', null, t('Please enter a YouTube URL', '請輸入 YouTube 網址'));
    return;
  }

  const url = youtubeUrl.value;
  const chunk = chunkDuration.value;
  closeAddModal();
  videoStore.setCreatingVideo(true, t('Starting...', '開始中...'));

  try {
    videoStore.updateCreateProgress(t('Downloading video...', '下載影片中...'));
    const response: VideoResponse = await videoService.createFromYouTube(url, chunk);
    videoStore.setCreatingVideo(false, '', response.video.id);
    videos.value.unshift(response.video);
    setTimeout(() => {
      goToVideo(response.video.id);
    }, 500);
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || t('Failed to create video', '創建影片失敗');
    videoStore.setCreatingVideo(false, '', null, errorMsg);
  }
}

async function fetchVideos() {
  isLoading.value = true;
  error.value = null;
  try {
    videos.value = await videoService.getAllVideos();
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load videos';
  } finally {
    isLoading.value = false;
  }
}

async function fetchDashboardStats() {
  statsLoading.value = true;
  try {
    const data = await statsService.getDashboardStats();
    dashboardStats.value = {
      wordsLearned: data.words_learned,
      hoursLearned: data.hours_learned,
      streakDays: data.streak_days,
      sentencesPracticed: data.sentences_practiced,
      dailyGoalMinutes: data.daily_goal_minutes,
      dailyGoalProgress: data.daily_goal_progress,
      dailyGoalRemaining: data.daily_goal_remaining,
      todayMinutes: data.today_minutes,
    };
  } catch (err: any) {
    console.error('Failed to fetch dashboard stats:', err);
  } finally {
    statsLoading.value = false;
  }
}

onMounted(() => {
  fetchVideos();
  fetchDashboardStats();
});

onActivated(() => {
  fetchDashboardStats();
});
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <main class="container mx-auto px-4 py-8">
      <div class="mb-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold font-display text-learning-text-primary mb-2">
            {{ t('Welcome back', '歡迎回來') }}！
          </h1>
          <p class="text-learning-text-secondary">{{ t('Continue your English learning journey', '繼續您的英語學習之旅') }}</p>
        </div>
        <button
          @click="openAddModal"
          class="flex items-center gap-2 px-4 py-2 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ t('Add Video', '添加影片') }}
        </button>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">{{ t('Words Learned', '已學詞匯') }}</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.wordsLearned }}</p>
        </div>

        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">{{ t('Hours Learned', '學習小時') }}</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.hoursLearned }}</p>
        </div>

        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-tertiary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">{{ t('Day Streak', '連續天數') }}</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.streakDays }}</p>
        </div>

        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">{{ t('Sentences', '句子的練習') }}</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.sentencesPracticed }}</p>
        </div>

        <div class="bg-gradient-to-br from-learning-accent-primary/10 to-learning-accent-secondary/10 rounded-xl p-5 border border-learning-accent-primary/20">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-primary" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <span class="text-learning-text-primary text-sm font-medium">{{ t('Daily Goal', '每日目標') }}</span>
          </div>
          <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden mb-2">
            <div class="h-full bg-gradient-to-r from-learning-accent-primary to-learning-accent-secondary rounded-full" :style="{ width: stats.dailyGoalProgress + '%' }" />
          </div>
          <p class="text-xs text-learning-text-muted">{{ t(`${stats.dailyGoalRemaining} min remaining`, `還剩${stats.dailyGoalRemaining}分鐘`) }}</p>
        </div>
      </div>

      <div class="mb-8">
        <h2 class="text-xl font-semibold font-display text-learning-text-primary mb-4">{{ t('Continue Learning', '繼續學習') }}</h2>

        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full"></div>
        </div>

        <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400">
          {{ error }}
        </div>

        <div v-else-if="videos.length === 0" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-8 text-center">
          <svg class="w-12 h-12 text-learning-text-muted mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <p class="text-learning-text-secondary mb-4">{{ t('No videos yet. Add a YouTube video to start learning!', '還沒有影片。添加 YouTube 影片開始學習！') }}</p>
          <button
            @click="openAddModal"
            class="px-4 py-2 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors"
          >
            {{ t('Add Your First Video', '添加您的第一個影片') }}
          </button>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="video in recentVideos"
            :key="video.id"
            @click="goToVideo(video.id)"
            class="bg-learning-surface rounded-xl overflow-hidden border border-learning-bg-tertiary cursor-pointer card-interactive group"
          >
            <div class="relative bg-learning-bg-primary h-40">
              <img :src="video.thumbnail" :alt="video.title" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-12 h-12 rounded-full bg-learning-accent-primary/90 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <svg class="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
              <span class="absolute bottom-2 right-2 px-2 py-0.5 bg-black/70 rounded text-xs text-white font-mono">
                {{ video.duration }}
              </span>
            </div>
            <div class="p-4">
              <h3 class="font-medium text-learning-text-primary mb-1 line-clamp-2">{{ video.title }}</h3>
              <div v-if="video.notes || video.notesZh" class="mt-2">
                <p v-if="video.notes" class="text-sm text-learning-text-secondary">{{ video.notes }}</p>
                <p v-if="languageStore.showZh && video.notesZh" class="text-sm text-learning-chinese">{{ video.notesZh }}</p>
              </div>
              <div class="flex items-center gap-2 mt-3">
                <div class="flex-1 h-1.5 bg-learning-bg-primary rounded-full overflow-hidden">
                  <div
                    class="h-full bg-learning-accent-primary rounded-full"
                    :style="{ width: `${video.progress}%` }"
                  />
                </div>
                <span class="text-xs text-learning-text-secondary">{{ video.progress }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showAddModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeAddModal">
      <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary w-full max-w-md p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold font-display text-learning-text-primary">{{ t('Add YouTube Video', '添加 YouTube 影片') }}</h3>
          <button @click="closeAddModal" class="text-learning-text-muted hover:text-learning-text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-learning-text-secondary mb-2">{{ t('YouTube URL', 'YouTube 網址') }}</label>
            <input
              ref="youtubeUrlInput"
              v-model="youtubeUrl"
              type="text"
              placeholder="https://www.youtube.com/watch?v=..."
              class="w-full px-4 py-3 bg-learning-bg-primary border border-learning-bg-tertiary rounded-lg text-learning-text-primary placeholder-learning-text-muted focus:outline-none focus:border-learning-accent-primary"
              @keyup.enter="createVideoFromYouTube"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-learning-text-secondary mb-2">{{ t('Chunk Size', '片段大小') }}</label>
            <div class="grid grid-cols-1 gap-2">
              <button
                v-for="option in chunkDurationOptions"
                :key="option.value"
                @click="chunkDuration = option.value"
                class="p-3 rounded-lg border text-left transition-all"
                :class="chunkDuration === option.value
                  ? 'border-learning-accent-primary bg-learning-accent-primary/10'
                  : 'border-learning-bg-tertiary hover:border-learning-accent-primary/50'"
              >
                <div class="flex items-center justify-between">
                  <span class="font-medium text-learning-text-primary">{{ option.label }}</span>
                  <span v-if="chunkDuration === option.value" class="text-learning-accent-primary">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                  </span>
                </div>
                <p class="text-xs text-learning-text-muted mt-1">{{ option.description }}</p>
              </button>
            </div>
          </div>

          <div class="flex gap-3 pt-2">
            <button
              @click="closeAddModal"
              class="flex-1 px-4 py-2 border border-learning-bg-tertiary text-learning-text-secondary hover:text-learning-text-primary rounded-lg transition-colors"
            >
              {{ t('Cancel', '取消') }}
            </button>
            <button
              @click="createVideoFromYouTube"
              class="flex-1 px-4 py-2 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
              :disabled="!youtubeUrl.trim()"
            >
              {{ t('Add Video', '添加影片') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>