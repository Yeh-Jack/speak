<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { videoService } from '@/services/video.service';
import { speakingService, type TranscriptSegment, type ComparisonResult } from '@/services/speaking.service';
import { useAuth } from '@/composables/useAuth';
import { useI18n } from '@/composables/useI18n';
import type { Video } from '@/types';

const router = useRouter();
const { user } = useAuth();
const { t } = useI18n();

type PracticePhase = 'select' | 'show' | 'play' | 'rollback' | 'record' | 'compare';

const videos = ref<Video[]>([]);
const selectedVideo = ref<Video | null>(null);
const videoStreamUrl = ref<string>('');
const segments = ref<TranscriptSegment[]>([]);
const selectedSegment = ref<TranscriptSegment | null>(null);
const currentPhase = ref<PracticePhase>('select');
const isLoading = ref(false);
const error = ref<string | null>(null);

const isRecording = ref(false);
const recordingTime = ref(0);
const mediaRecorder = ref<MediaRecorder | null>(null);
const audioChunks = ref<Blob[]>([]);
const recordedBlob = ref<Blob | null>(null);

const comparisonResult = ref<ComparisonResult | null>(null);

const audioElement = ref<HTMLAudioElement | null>(null);
const playbackStartTime = ref(0);

const practiceHistory = ref<Array<{ id: string; title: string; score: number; date: string }>>([]);

const canProceedToPlay = computed(() => selectedSegment.value !== null);
const canProceedToRecord = computed(() => currentPhase.value === 'rollback');

async function loadVideos() {
  isLoading.value = true;
  error.value = null;
  try {
    videos.value = await videoService.getAllVideos();
  } catch (err: any) {
    error.value = err.message || 'Failed to load videos';
  } finally {
    isLoading.value = false;
  }
}

async function selectVideo(video: Video) {
  selectedVideo.value = video;
  videoStreamUrl.value = await videoService.getStreamUrl(video.id);
  isLoading.value = true;
  error.value = null;
  try {
    const response = await speakingService.getVideoSegments(video.id);
    segments.value = response.segments;
  } catch (err: any) {
    error.value = err.message || 'Failed to load transcript';
    segments.value = [];
  } finally {
    isLoading.value = false;
  }
}

function selectSegment(segment: TranscriptSegment) {
  selectedSegment.value = segment;
  currentPhase.value = 'show';
  comparisonResult.value = null;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

async function proceedToPlay() {
  if (!selectedSegment.value || !selectedVideo.value) return;
  currentPhase.value = 'play';
  playbackStartTime.value = selectedSegment.value.start;
  await playAudio();
}

async function playAudio() {
  if (!selectedSegment.value || !videoStreamUrl.value) return;

  audioElement.value = new Audio(videoStreamUrl.value);
  audioElement.value.currentTime = selectedSegment.value.start;

  audioElement.value.onended = () => {
    if (currentPhase.value === 'play') {
      proceedToRollback();
    }
  };

  try {
    await audioElement.value.play();
  } catch (err) {
    console.error('Audio playback failed:', err);
    setTimeout(() => proceedToRollback(), 1000);
  }
}

function proceedToRollback() {
  if (!selectedSegment.value) return;
  currentPhase.value = 'rollback';

  if (audioElement.value) {
    const rollbackTime = Math.max(0, selectedSegment.value.start - 3);
    audioElement.value.currentTime = rollbackTime;
  }

  setTimeout(() => {
    currentPhase.value = 'record';
    startRecording();
  }, 1500);
}

async function startRecording() {
  if (!selectedSegment.value) return;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.value = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    audioChunks.value = [];

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    };

    mediaRecorder.value.onstop = async () => {
      recordedBlob.value = new Blob(audioChunks.value, { type: 'audio/webm' });
      stream.getTracks().forEach((track) => track.stop());
      await submitRecording();
    };

    mediaRecorder.value.start();
    isRecording.value = true;
    recordingTime.value = 0;

    const duration = selectedSegment.value.end - selectedSegment.value.start;
    const timer = setInterval(() => {
      recordingTime.value++;
      if (recordingTime.value >= duration) {
        stopRecording();
        clearInterval(timer);
      }
    }, 1000);
  } catch (err) {
    console.error('Failed to start recording:', err);
    error.value = 'Microphone access denied';
  }
}

function stopRecording() {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop();
    isRecording.value = false;
  }
}

async function submitRecording() {
  if (!recordedBlob.value || !selectedVideo.value || !selectedSegment.value) return;

  isLoading.value = true;
  error.value = null;

  try {
    comparisonResult.value = await speakingService.compareRecording(
      selectedVideo.value.id,
      selectedSegment.value.start,
      selectedSegment.value.end,
      recordedBlob.value
    );
    currentPhase.value = 'compare';

    practiceHistory.value.unshift({
      id: Date.now().toString(),
      title: selectedSegment.value.text.substring(0, 30) + '...',
      score: Math.round(comparisonResult.value.similarity_score * 100),
      date: new Date().toISOString().split('T')[0],
    });
  } catch (err: any) {
    error.value = err.message || 'Failed to compare recording';
  } finally {
    isLoading.value = false;
  }
}

function retryRecording() {
  comparisonResult.value = null;
  currentPhase.value = 'rollback';
  recordedBlob.value = null;

  setTimeout(() => {
    currentPhase.value = 'record';
    startRecording();
  }, 500);
}

function nextSegment() {
  if (!selectedSegment.value) return;
  const currentIndex = segments.value.findIndex(
    (s) => s.start === selectedSegment.value?.start && s.end === selectedSegment.value?.end
  );
  if (currentIndex < segments.value.length - 1) {
    selectSegment(segments.value[currentIndex + 1]);
  } else {
    resetPractice();
  }
}

function resetPractice() {
  currentPhase.value = 'select';
  selectedSegment.value = null;
  comparisonResult.value = null;
  recordedBlob.value = null;
  selectedVideo.value = null;
  segments.value = [];
}

function playUserRecording() {
  if (!recordedBlob.value) return;
  const url = URL.createObjectURL(recordedBlob.value);
  const audio = new Audio(url);
  audio.play();
}

function playOriginalAudio() {
  if (!videoStreamUrl.value || !selectedSegment.value) return;
  audioElement.value = new Audio(videoStreamUrl.value);
  audioElement.value.currentTime = selectedSegment.value.start;
  audioElement.value.play();
}

onMounted(() => {
  loadVideos();
});

onUnmounted(() => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop();
  }
  if (audioElement.value) {
    audioElement.value.pause();
  }
});
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <main class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold font-display text-learning-text-primary mb-2">
          {{ t('Character Impersonation', '角色模仿') }}
        </h1>
        <p class="text-learning-text-secondary">
          {{ t('Practice speaking like a character from your video', '練習像影片中的角色一樣說話') }}
        </p>
      </div>

      <div v-if="error" class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 mb-6">
        {{ error }}
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <div v-if="currentPhase === 'select'" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6">
            <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              {{ t('Select a Video', '選擇影片') }}
            </h2>

            <div v-if="isLoading && videos.length === 0" class="flex items-center justify-center py-12">
              <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full"></div>
            </div>

            <div v-else-if="videos.length === 0" class="text-center py-12">
              <p class="text-learning-text-secondary mb-4">{{ t('No videos available. Add a video to start practicing!', '還沒有影片。添加影片開始練習！') }}</p>
              <router-link to="/" class="px-4 py-2 bg-learning-accent-primary text-white rounded-lg">
                {{ t('Go to Dashboard', '前往儀表板') }}
              </router-link>
            </div>

            <div v-else class="grid grid-cols-2 gap-4">
              <button
                v-for="video in videos"
                :key="video.id"
                @click="selectVideo(video)"
                class="p-4 rounded-xl border transition-all text-left"
                :class="selectedVideo?.id === video.id
                  ? 'border-learning-accent-primary bg-learning-accent-primary/10'
                  : 'border-learning-bg-tertiary hover:border-learning-accent-primary/50'"
              >
                <img
                  :src="video.thumbnail || `https://picsum.photos/seed/${video.id}/320/180`"
                  :alt="video.title"
                  class="w-full aspect-video object-cover rounded-lg mb-2"
                />
                <h3 class="font-medium text-learning-text-primary text-sm line-clamp-2">{{ video.title }}</h3>
                <p class="text-xs text-learning-text-muted">{{ formatTime(video.duration) }}</p>
              </button>
            </div>
          </div>

          <div v-else-if="segments.length > 0 && currentPhase !== 'compare'" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold font-display text-learning-text-primary">
                {{ t('Select a Line', '選擇台詞') }}
              </h2>
              <button @click="resetPractice" class="text-sm text-learning-text-muted hover:text-learning-text-primary">
                {{ t('← Back', '← 返回') }}
              </button>
            </div>

            <div class="space-y-2 max-h-96 overflow-y-auto">
              <button
                v-for="(segment, index) in segments"
                :key="index"
                @click="selectSegment(segment)"
                class="w-full p-3 rounded-lg border text-left transition-all"
                :class="selectedSegment?.start === segment.start
                  ? 'border-learning-accent-primary bg-learning-accent-primary/10'
                  : 'border-learning-bg-tertiary hover:border-learning-accent-primary/50'"
              >
                <p class="text-learning-text-primary text-sm">{{ segment.text }}</p>
                <p class="text-xs text-learning-text-muted mt-1">
                  {{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}
                </p>
              </button>
            </div>
          </div>

          <div v-else-if="currentPhase !== 'compare'" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6">
            <div class="flex items-center justify-center py-12">
              <div class="text-center">
                <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                <p class="text-learning-text-secondary">{{ t('Loading transcript...', '載入字幕中...') }}</p>
              </div>
            </div>
          </div>

          <div v-if="selectedSegment && currentPhase !== 'select' && currentPhase !== 'compare'" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6 mt-6">
            <div class="text-center mb-6">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-learning-accent-primary/10 rounded-full text-learning-accent-primary mb-4">
                <span v-if="currentPhase === 'show'">{{ t('1. SHOW', '1. 顯示') }}</span>
                <span v-else-if="currentPhase === 'play'">{{ t('2. PLAY', '2. 播放') }}</span>
                <span v-else-if="currentPhase === 'rollback'">{{ t('3. ROLLBACK', '3. 回放') }}</span>
                <span v-else-if="currentPhase === 'record'">{{ t('4. RECORD', '4. 錄製') }}</span>
              </div>

              <div class="bg-learning-bg-primary rounded-xl p-8 mb-6">
                <p class="text-2xl font-medium text-learning-text-primary leading-relaxed">
                  "{{ selectedSegment.text }}"
                </p>
                <p class="text-sm text-learning-text-muted mt-4">
                  {{ formatTime(selectedSegment.start) }} - {{ formatTime(selectedSegment.end) }}
                </p>
              </div>

              <div v-if="currentPhase === 'record' && isRecording" class="mb-4">
                <div class="flex justify-center gap-1">
                  <div
                    v-for="i in 8"
                    :key="i"
                    class="w-2 bg-red-500 rounded-full animate-pulse"
                    :style="{
                      height: `${20 + Math.random() * 40}px`,
                      animationDelay: `${i * 0.1}s`
                    }"
                  />
                </div>
                <p class="text-red-400 mt-2">{{ t('Recording...', '錄製中...') }} {{ recordingTime }}s</p>
              </div>

              <div class="flex justify-center gap-4">
                <button
                  v-if="currentPhase === 'record'"
                  @click="stopRecording"
                  class="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg transition-colors"
                >
                  {{ t('Stop Recording', '停止錄製') }}
                </button>
                <button
                  v-else-if="currentPhase === 'show'"
                  @click="proceedToPlay"
                  class="px-6 py-3 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors"
                >
                  {{ t('Play Original Audio →', '播放原始音頻 →') }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="currentPhase === 'compare' && comparisonResult" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6 mt-6">
            <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-6 text-center">
              {{ t('Comparison Results', '比較結果') }}
            </h2>

            <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="bg-learning-bg-primary rounded-xl p-4">
                <h3 class="text-sm font-medium text-learning-text-secondary mb-2">{{ t('Original', '原始') }}</h3>
                <p class="text-learning-text-primary">{{ comparisonResult.original_text }}</p>
                <button @click="playOriginalAudio" class="mt-2 text-sm text-learning-accent-primary hover:underline">
                  {{ t('▶ Play', '▶ 播放') }}
                </button>
              </div>
              <div class="bg-learning-bg-primary rounded-xl p-4">
                <h3 class="text-sm font-medium text-learning-text-secondary mb-2">{{ t('Your Recording', '你的錄音') }}</h3>
                <p class="text-learning-text-primary">{{ comparisonResult.user_text }}</p>
                <button @click="playUserRecording" class="mt-2 text-sm text-learning-accent-primary hover:underline">
                  {{ t('▶ Play', '▶ 播放') }}
                </button>
              </div>
            </div>

            <div class="text-center mb-6">
              <div class="inline-flex items-center justify-center w-24 h-24 rounded-full border-4 mb-4"
                :class="comparisonResult.similarity_score >= 0.7 ? 'border-green-500' : comparisonResult.similarity_score >= 0.4 ? 'border-yellow-500' : 'border-red-500'">
                <span class="text-3xl font-bold text-learning-text-primary">
                  {{ Math.round(comparisonResult.similarity_score * 100) }}%
                </span>
              </div>
              <p class="text-learning-text-secondary">{{ comparisonResult.feedback }}</p>
            </div>

            <div class="flex justify-center gap-4">
              <button
                @click="retryRecording"
                class="px-6 py-3 border border-learning-bg-tertiary text-learning-text-secondary hover:text-learning-text-primary font-medium rounded-lg transition-colors"
              >
                {{ t('Try Again', '再試一次') }}
              </button>
              <button
                @click="nextSegment"
                class="px-6 py-3 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors"
              >
                {{ t('Next Line →', '下一句 →') }}
              </button>
            </div>
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6 mt-6">
            <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              {{ t('Practice Tips', '練習技巧') }}
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="p-4 bg-learning-bg-primary rounded-lg">
                <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center mb-3">
                  <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                </div>
                <h3 class="font-medium text-learning-text-primary mb-1">{{ t('Listen Carefully', '仔細聆聽') }}</h3>
                <p class="text-sm text-learning-text-muted">{{ t('Pay attention to tone and rhythm', '注意語調和節奏') }}</p>
              </div>
              <div class="p-4 bg-learning-bg-primary rounded-lg">
                <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center mb-3">
                  <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 class="font-medium text-learning-text-primary mb-1">{{ t('Speak Clearly', '清晰說話') }}</h3>
                <p class="text-sm text-learning-text-muted">{{ t('Pronounce each word distinctly', '每個單詞發音清晰') }}</p>
              </div>
              <div class="p-4 bg-learning-bg-primary rounded-lg">
                <div class="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-3">
                  <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 class="font-medium text-learning-text-primary mb-1">{{ t('Practice Daily', '每日練習') }}</h3>
                <p class="text-sm text-learning-text-muted">{{ t('Consistency builds fluency', '堅持練習才能流利') }}</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5 mb-6">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              {{ t('Recent Practice', '最近練習') }}
            </h3>
            <div v-if="practiceHistory.length === 0" class="text-center py-6">
              <p class="text-sm text-learning-text-muted">{{ t('No practice sessions yet', '還沒有練習記錄') }}</p>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="session in practiceHistory.slice(0, 5)"
                :key="session.id"
                class="p-3 bg-learning-bg-primary rounded-lg"
              >
                <div class="flex items-start justify-between mb-2">
                  <h4 class="font-medium text-learning-text-primary text-sm line-clamp-1">{{ session.title }}</h4>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :class="session.score >= 70 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'"
                  >
                    {{ session.score }}%
                  </span>
                </div>
                <div class="flex items-center gap-3 text-xs text-learning-text-muted">
                  <span>{{ session.date }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              {{ t('How It Works', '如何運作') }}
            </h3>
            <div class="space-y-3 text-sm">
              <div class="flex gap-3">
                <div class="w-6 h-6 rounded-full bg-learning-accent-primary/10 flex items-center justify-center flex-shrink-0">
                  <span class="text-xs font-medium text-learning-accent-primary">1</span>
                </div>
                <p class="text-learning-text-secondary">{{ t('Select a video and line to practice', '選擇影片和句子練習') }}</p>
              </div>
              <div class="flex gap-3">
                <div class="w-6 h-6 rounded-full bg-learning-accent-primary/10 flex items-center justify-center flex-shrink-0">
                  <span class="text-xs font-medium text-learning-accent-primary">2</span>
                </div>
                <p class="text-learning-text-secondary">{{ t('Listen to the character speak', '聽角色說話') }}</p>
              </div>
              <div class="flex gap-3">
                <div class="w-6 h-6 rounded-full bg-learning-accent-primary/10 flex items-center justify-center flex-shrink-0">
                  <span class="text-xs font-medium text-learning-accent-primary">3</span>
                </div>
                <p class="text-learning-text-secondary">{{ t('Record yourself imitating', '錄製您的模仿') }}</p>
              </div>
              <div class="flex gap-3">
                <div class="w-6 h-6 rounded-full bg-learning-accent-primary/10 flex items-center justify-center flex-shrink-0">
                  <span class="text-xs font-medium text-learning-accent-primary">4</span>
                </div>
                <p class="text-learning-text-secondary">{{ t('Get AI feedback on your pronunciation', '獲得AI發音反饋') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>