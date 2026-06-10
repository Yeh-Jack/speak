<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useVideoStore } from '@/stores';
import { useLanguageStore } from '@/stores/language.store';
import { useI18n } from '@/composables/useI18n';
import { videoService } from '@/services/video.service';
import { statsService } from '@/services/stats.service';
import VideoPlayer from '@/components/video/VideoPlayer.vue';
import StudyPlanDisplay from '@/components/learning/StudyPlanDisplay.vue';
import VocabularyCard from '@/components/learning/VocabularyCard.vue';
import ShadowingMode from '@/components/learning/ShadowingMode.vue';
import type { TranscriptSegment } from '@/types';

const route = useRoute();
const videoStore = useVideoStore();
const languageStore = useLanguageStore();
const { t } = useI18n();

const videoId = computed(() => route.params.id as string);

const showShadowingMode = ref(false);
const showVocabularyReview = ref(false);
const showGrammarNotes = ref(false);
const showFavoriteVocabulary = ref(false);
const videoRef = ref<InstanceType<typeof VideoPlayer> | null>(null);
const currentTime = ref(0);
const isLoading = ref(false);
const error = ref<string | null>(null);
const videoSrc = ref('');
const videoStatus = ref<'idle' | 'loading' | 'ready' | 'error'>('idle');

watch(() => videoStore.currentChunkIndex, (newIndex) => {
  const chunk = videoStore.chunks[newIndex];
  if (chunk && videoRef.value) {
    videoRef.value.seek(chunk.start_time);
  }
  saveProgress();
});

let saveProgressInterval: ReturnType<typeof setInterval> | null = null;

onMounted(() => {
  videoStore.reset();
  fetchVideoData();
  videoStore.loadReviewedVocabulary();
  videoStore.loadFavoriteVocabulary();
  saveProgressInterval = setInterval(() => {
    if (videoRef.value && videoStore.currentVideo) {
      saveProgress();
    }
  }, 30000);
});

onUnmounted(() => {
  saveProgress();
  if (saveProgressInterval) {
    clearInterval(saveProgressInterval);
  }
});

const currentTranscriptSegments = computed((): TranscriptSegment[] => {
  return videoStore.currentTranscript?.segments || [];
});

const SENTENCE_END_REGEX = /[.!?]['"]*$/;

const shadowingSentences = computed(() => {
  const sentences: Array<{
    id: string;
    text: string;
    startTime: number;
    endTime: number;
    translation?: string;
    chunkIndex: number;
  }> = [];

  let currentText = '';
  let currentStartTime = 0;
  let currentEndTime = 0;

  const segments = currentTranscriptSegments.value;
  
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    
    if (!currentText) {
      currentStartTime = seg.start;
    }
    currentText += (currentText ? ' ' : '') + seg.text;
    currentEndTime = seg.end;

    const trimmedText = currentText.trim();
    if (SENTENCE_END_REGEX.test(trimmedText)) {
      const nextSeg = segments[i + 1];
      const sentenceEndTime = nextSeg ? nextSeg.start : seg.end;
      
      const chunkIndex = videoStore.chunks.findIndex((chunk) => {
        const tolerance = 1;
        return currentStartTime >= chunk.start_time - tolerance &&
               sentenceEndTime <= chunk.end_time + tolerance;
      });

      sentences.push({
        id: `sentence-${sentences.length}`,
        text: trimmedText,
        startTime: currentStartTime,
        endTime: sentenceEndTime,
        translation: trimmedText,
        chunkIndex: chunkIndex >= 0 ? chunkIndex : videoStore.currentChunkIndex,
      });

      currentText = '';
    }
  }

  if (currentText.trim()) {
    const chunkIndex = videoStore.chunks.findIndex((chunk) => {
      const tolerance = 1;
      return currentStartTime >= chunk.start_time - tolerance &&
             currentEndTime <= chunk.end_time + tolerance;
    });

    sentences.push({
      id: `sentence-${sentences.length}`,
      text: currentText.trim(),
      startTime: currentStartTime,
      endTime: currentEndTime,
      translation: currentText.trim(),
      chunkIndex: chunkIndex >= 0 ? chunkIndex : videoStore.currentChunkIndex,
    });
  }

  return sentences;
});

const studyPlanProps = computed(() => {
  const plan = videoStore.currentStudyPlan;
  console.log('VideoPlayerView studyPlanProps: currentStudyPlan is', plan ? 'truthy' : 'falsy');
  if (!plan) {
    console.log('VideoPlayerView: currentStudyPlan is null');
    return null;
  }
  
  const result = {
    plan: {
      objectives: plan.objectives || [],
      vocabulary: plan.vocabulary || [],
      grammar: plan.grammar || [],
      totalChunks: videoStore.totalChunks || 1,
      completedChunks: videoStore.completedObjectives || 0,
      estimatedMinutes: parseInt(plan.estimated_time || '0', 10) || 30,
    },
    currentChunkIndex: videoStore.currentChunkIndex || 0,
  };
  
  console.log('VideoPlayerView: studyPlanProps computed', {
    hasVocabulary: result.plan.vocabulary.length > 0,
    vocabularyCount: result.plan.vocabulary.length,
    hasGrammar: result.plan.grammar.length > 0,
    grammarCount: result.plan.grammar.length,
    totalChunks: result.plan.totalChunks
  });
  
  return result;
});

function handleTimeUpdate(time: number) {
  currentTime.value = time;
  const chunkIndex = videoStore.chunks.findIndex((chunk, index) => {
    const nextChunk = videoStore.chunks[index + 1];
    const isLastChunk = index === videoStore.chunks.length - 1;
    if (isLastChunk) {
      return time >= chunk.start_time;
    }
    return time >= chunk.start_time && time < (nextChunk?.start_time ?? Infinity);
  });
  if (chunkIndex !== -1 && chunkIndex !== videoStore.currentChunkIndex) {
    videoStore.setCurrentChunkIndex(chunkIndex);
  }
}

function handleVocabularyPlay(word: string) {
  const utterance = new SpeechSynthesisUtterance(word);
  utterance.lang = 'en-US';
  utterance.rate = 0.7;
  speechSynthesis.speak(utterance);
}

function handleVocabularySave(word: string) {
  videoStore.toggleVocabularySave(word);
}

async function handleMarkReviewed(word: string) {
  try {
    await videoService.reviewVocabulary(word);
    videoStore.markVocabularyReviewed(word);
  } catch (err) {
    console.error('Failed to mark vocabulary as reviewed:', err);
  }
}

function handleStartLearning() {
  showShadowingMode.value = true;
}

function handleSentenceComplete(sentenceId: string) {
  console.log('Sentence completed:', sentenceId);
}

function handlePracticeComplete() {
  showShadowingMode.value = false;
}

function handleToggleObjective(objectiveId: string) {
  videoStore.toggleObjective(objectiveId);
  const plan = videoStore.currentStudyPlan;
  if (plan) {
    const objectiveUpdates = plan.objectives.map(obj => ({
      id: obj.id,
      completed: obj.completed,
    }));
    videoService.updateStudyPlanObjective(videoId.value, plan.chunk_index ?? -1, objectiveUpdates);
  }
}

function handleSelectObjective(objectiveId: string) {
  const objective = videoStore.studyObjectives.find(obj => obj.id === objectiveId);
  if (!objective) return;
  switch (objective.type) {
    case 'vocabulary':
      showVocabularyReview.value = true;
      break;
    case 'grammar':
      showGrammarNotes.value = true;
      break;
    case 'speaking':
      showShadowingMode.value = true;
      break;
    default:
      break;
  }
}

async function fetchVideoData() {
  isLoading.value = true;
  error.value = null;
  videoStatus.value = 'loading';

  try {
    const video = await videoService.getVideo(videoId.value);
    videoStore.setVideo(video);

    const chunks = await videoService.getChunks(videoId.value);
    videoStore.setChunks(chunks);

    const priorityTypes = ['user', 'youtube_author', 'whisper', 'youtube_auto'] as const;
    for (const type of priorityTypes) {
      try {
        const transcript = await videoService.getTranscript(videoId.value, type);
        videoStore.setTranscript(type, transcript);
        break;
      } catch {
        continue;
      }
    }

    try {
      const studyPlans = await videoService.getStudyPlans(videoId.value);
      console.log('getStudyPlans returned:', studyPlans.length, 'study plans');
      if (studyPlans.length > 0) {
        console.log('Setting study plan, vocabulary count:', studyPlans[0].vocabulary?.length);
        videoStore.setStudyPlan(studyPlans[0]);
      } else {
        console.warn('No study plans found for video:', videoId.value);
      }
    } catch (err: any) {
      console.error('Failed to fetch study plans:', err.response?.data || err.message);
    }

    videoSrc.value = await videoService.getStreamUrl(videoId.value);

    const resumeInfo = await videoService.getProgress(videoId.value);
    if (resumeInfo && resumeInfo.timestamp > 0) {
      videoStore.setCurrentChunkIndex(resumeInfo.chunk_index);
      await nextTick();
      if (videoRef.value) {
        videoRef.value.seek(resumeInfo.timestamp);
      }
    }

    videoStatus.value = 'ready';
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load video';
    videoStatus.value = 'error';
  } finally {
    isLoading.value = false;
  }
}

async function saveProgress() {
  if (!videoRef.value || !videoStore.currentVideo) return;
  try {
    const currentTime = videoRef.value.getCurrentTime();
    await videoService.saveProgress(videoId.value, videoStore.currentChunkIndex, currentTime);
  } catch (err) {
    console.error('Failed to save progress:', err);
  }
}

onMounted(() => {
  videoStore.reset();
  fetchVideoData();
});
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <main class="container mx-auto px-4 py-6">
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full mr-4"></div>
        <span class="text-learning-text-secondary">{{ t('Loading video...', '載入中...') }}</span>
      </div>

      <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-red-400 text-center">
        {{ error }}
        <div class="mt-4">
          <router-link
            to="/"
            class="px-4 py-2 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors inline-block"
          >
            Back to Dashboard
          </router-link>
        </div>
      </div>

      <template v-else-if="videoStore.currentVideo">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary overflow-hidden">
              <VideoPlayer
                v-if="videoSrc"
                ref="videoRef"
                :src="videoSrc"
                :transcript="currentTranscriptSegments"
                :show-zh="languageStore.showZh"
                @time-update="handleTimeUpdate"
                @paused="saveProgress"
              />
              <div v-else class="aspect-video flex items-center justify-center bg-learning-bg-primary">
                <div class="text-center">
                  <p class="text-learning-text-secondary mb-2">Video not available for streaming</p>
                  <p class="text-sm text-learning-text-muted">The video may still be processing or is not available in a streamable format.</p>
                </div>
              </div>
            </div>

            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold font-display text-learning-text-primary flex items-center gap-2">
                  <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  {{ t('Chunks', '片段') }}
                </h3>
                <span class="text-sm text-learning-text-secondary">
                  {{ videoStore.currentChunkIndex + 1 }} / {{ videoStore.chunks.length }}
                </span>
              </div>
              <div class="flex gap-2 flex-wrap">
                <button
                  v-for="(chunk, index) in videoStore.chunks"
                  :key="chunk.id"
                  @click="videoStore.setCurrentChunkIndex(index)"
                  class="px-3 py-2 rounded-lg text-sm font-medium transition-all text-center leading-tight min-w-[3.5rem]"
                  :class="videoStore.currentChunkIndex === index
                    ? 'bg-learning-accent-primary text-white'
                    : 'bg-learning-bg-primary text-learning-text-secondary hover:bg-learning-surface-hover'"
                >
                  <span class="block">{{ index + 1 }}</span>
                  <span class="block text-xs opacity-70 font-mono">{{ Math.floor(chunk.start_time / 60).toString().padStart(2, '0') }}:{{ Math.floor(chunk.start_time % 60).toString().padStart(2, '0') }}</span>
                </button>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="vocab in videoStore.vocabularyItems.slice(0, 4)"
                :key="vocab.word"
                class="card-interactive"
              >
                <VocabularyCard
                  :word="vocab.word"
                  :word-zh="vocab.word_zh"
                  :definition="vocab.definition"
                  :definition-zh="vocab.definition_zh"
                  :context="vocab.context"
                  :context-zh="vocab.context_zh"
                  :cefr-level="vocab.cefr_level"
                  :cefr-level-zh="vocab.cefr_level_zh"
                  :pronunciation="vocab.pronunciation"
                  :examples="vocab.examples"
                  :examples-zh="vocab.examples_zh"
                  :is-saved="videoStore.isVocabularySaved(vocab.word)"
                  :show-zh="languageStore.showZh"
                  :is-reviewed="videoStore.isVocabularyReviewed(vocab.word)"
                  @play-audio="handleVocabularyPlay"
                  @save-word="handleVocabularySave"
                  @mark-reviewed="handleMarkReviewed"
                />
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4 flex items-center gap-2">
                <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                {{ t('Quick Actions', '快速操作') }}
              </h3>
              <div class="space-y-3">
                <button
                  v-spray
                  @click="showShadowingMode = !showShadowingMode"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary rounded-lg transition-colors text-left"
                  :class="showShadowingMode ? 'ring-2 ring-learning-accent-primary' : ''"
                >
                  <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-learning-text-primary">{{ t('Shadowing Mode', '跟讀模式') }}</p>
                    <p class="text-sm text-learning-text-secondary">{{ t('Practice speaking', '練習口說') }}</p>
                  </div>
                  <svg
                    class="w-5 h-5 text-learning-text-muted transition-transform"
                    :class="showShadowingMode ? 'rotate-180' : ''"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <Transition
                    enter-active-class="transition-all duration-300 ease-out"
                    enter-from-class="max-h-0 opacity-0 -translate-y-2"
                    enter-to-class="max-h-[500px] opacity-100 translate-y-0"
                    leave-active-class="transition-all duration-200 ease-in"
                    leave-from-class="max-h-[500px] opacity-100 translate-y-0"
                    leave-to-class="max-h-0 opacity-0 -translate-y-2"
                  >
                    <div v-if="showShadowingMode" class="mt-4 overflow-hidden rounded-lg">
                      <ShadowingMode
                        :sentences="shadowingSentences"
                        :video-id="videoId"
                        :is-active="showShadowingMode"
                        @sentence-complete="handleSentenceComplete"
                        @practice-complete="handlePracticeComplete"
                        @close="showShadowingMode = false"
                      />
                    </div>
                  </Transition>

                <button
                  v-spray
                  @click="showFavoriteVocabulary = !showFavoriteVocabulary"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary rounded-lg transition-colors text-left"
                  :class="showFavoriteVocabulary ? 'ring-2 ring-learning-accent-primary' : ''"
                >
                  <div class="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-learning-text-primary">{{ t('Favorite Vocabulary', '收藏詞匯') }}</p>
                    <p class="text-sm text-learning-text-secondary">{{ videoStore.favoriteVocabularyCount }} {{ t('items', '項') }}</p>
                  </div>
                  <svg
                    class="w-5 h-5 text-learning-text-muted transition-transform"
                    :class="showFavoriteVocabulary ? 'rotate-180' : ''"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                <Transition
                    enter-active-class="transition-all duration-300 ease-out"
                    enter-from-class="max-h-0 opacity-0 -translate-y-2"
                    enter-to-class="max-h-[500px] opacity-100 translate-y-0"
                    leave-active-class="transition-all duration-200 ease-in"
                    leave-from-class="max-h-[500px] opacity-100 translate-y-0"
                    leave-to-class="max-h-0 opacity-0 -translate-y-2"
                  >
                    <div v-if="showFavoriteVocabulary" class="mt-4 p-4 bg-learning-bg-expanded rounded-lg overflow-hidden">
                      <div v-if="videoStore.favoriteVocabularyCount === 0" class="text-center text-learning-text-muted text-sm py-4">
                        {{ t('No favorite vocabulary yet. Click the star on any word to add it here.', '尚無收藏詞匯。點擊任意單詞的星號添加到這裡。') }}
                      </div>
                      <div v-else class="flex flex-wrap gap-2">
                        <span
                          v-for="word in Array.from(videoStore.favoriteVocabulary)"
                          :key="word"
                          class="px-3 py-1 bg-learning-accent-secondary/20 text-learning-accent-secondary rounded-full text-sm"
                        >
                          {{ word }}
                        </span>
                      </div>
                    </div>
                  </Transition>

                <button
                  v-spray
                  @click="showVocabularyReview = true"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary rounded-lg transition-colors text-left"
                >
                  <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-learning-text-primary">{{ t('Review Vocabulary', '複習詞匯') }}</p>
                    <p class="text-sm text-learning-text-secondary">{{ t(`${videoStore.savedVocabulary.size} saved`, `${videoStore.savedVocabulary.size} 已收藏`) }}</p>
                  </div>
                </button>

                <button
                  v-spray
                  @click="showGrammarNotes = true"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary rounded-lg transition-colors text-left"
                >
                  <div class="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-learning-text-primary">{{ t('Grammar Notes', '文法筆記') }}</p>
                    <p class="text-sm text-learning-text-secondary">{{ t(`${videoStore.grammarItems.length} patterns`, `${videoStore.grammarItems.length} 句型`) }}</p>
                  </div>
                </button>
              </div>
            </div>

            <StudyPlanDisplay
              v-if="studyPlanProps"
              :plan="studyPlanProps.plan"
              :current-chunk-index="studyPlanProps.currentChunkIndex"
              :show-zh="languageStore.showZh"
              @start-learning="handleStartLearning"
              @toggle-objective="handleToggleObjective"
              @select-objective="handleSelectObjective"
            />

            <div v-else class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
                {{ t('Study Plan', '學習計劃') }}
              </h3>
              <p class="text-learning-text-secondary text-sm">
                {{ t('No study plan available for this video yet.', '此影片尚無學習計劃。') }}
              </p>
            </div>

            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
                {{ t('Progress', '進度') }}
              </h3>
              <div class="space-y-4">
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-learning-text-secondary">{{ t('Vocabulary learned', '詞匯已學') }}</span>
                    <span class="text-learning-text-primary">{{ videoStore.reviewedVocabularyCount }} / {{ videoStore.vocabularyItems.length }}</span>
                  </div>
                  <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                    <div
                      class="h-full bg-learning-accent-secondary rounded-full"
                      :style="{ width: `${videoStore.vocabularyItems.length > 0 ? (videoStore.reviewedVocabularyCount / videoStore.vocabularyItems.length) * 100 : 0}%` }"
                    />
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-learning-text-secondary">{{ t('Shadowing practice', '跟讀練習') }}</span>
                    <span class="text-learning-text-primary">{{ videoStore.completedObjectives }} / {{ shadowingSentences.length }}</span>
                  </div>
                  <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                    <div
                      class="h-full bg-learning-accent-primary rounded-full"
                      :style="{ width: `${shadowingSentences.length > 0 ? (videoStore.completedObjectives / shadowingSentences.length) * 100 : 0}%` }"
                    />
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-learning-text-secondary">{{ t('Grammar patterns', '文法句型') }}</span>
                    <span class="text-learning-text-primary">{{ videoStore.completedObjectives }} / {{ videoStore.grammarItems.length }}</span>
                  </div>
                  <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                    <div
                      class="h-full bg-purple-400 rounded-full"
                      :style="{ width: `${videoStore.grammarItems.length > 0 ? (videoStore.completedObjectives / videoStore.grammarItems.length) * 100 : 0}%` }"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>

    <div v-if="showVocabularyReview" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showVocabularyReview = false">
      <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary w-full max-w-2xl max-h-[80vh] overflow-hidden">
        <div class="p-5 border-b border-learning-bg-tertiary flex items-center justify-between">
          <h3 class="text-xl font-semibold font-display text-learning-text-primary">{{ t('Vocabulary Review', '詞匯複習') }}</h3>
          <button @click="showVocabularyReview = false" class="text-learning-text-muted hover:text-learning-text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[60vh]">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="vocab in videoStore.vocabularyItems" :key="vocab.word" class="card-interactive">
              <VocabularyCard
                :word="vocab.word"
                :word-zh="vocab.word_zh"
                :definition="vocab.definition"
                :definition-zh="vocab.definition_zh"
                :context="vocab.context"
                :context-zh="vocab.context_zh"
                :cefr-level="vocab.cefr_level"
                :cefr-level-zh="vocab.cefr_level_zh"
                :pronunciation="vocab.pronunciation"
                :examples="vocab.examples"
                :examples-zh="vocab.examples_zh"
                :is-saved="videoStore.isVocabularySaved(vocab.word)"
                :is-reviewed="videoStore.isVocabularyReviewed(vocab.word)"
                @play-audio="handleVocabularyPlay"
                @save-word="handleVocabularySave"
                @mark-reviewed="handleMarkReviewed"
              />
            </div>
          </div>
          <p v-if="videoStore.vocabularyItems.length === 0" class="text-center text-learning-text-muted py-8">
            No vocabulary items available for this video.
          </p>
        </div>
      </div>
    </div>

    <div v-if="showGrammarNotes" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showGrammarNotes = false">
      <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary w-full max-w-2xl max-h-[80vh] overflow-hidden">
        <div class="p-5 border-b border-learning-bg-tertiary flex items-center justify-between">
          <h3 class="text-xl font-semibold font-display text-learning-text-primary">{{ t('Grammar Notes', '文法筆記') }}</h3>
          <button @click="showGrammarNotes = false" class="text-learning-text-muted hover:text-learning-text-primary">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-5 overflow-y-auto max-h-[60vh]">
          <div class="space-y-4">
            <div v-for="(grammar, index) in videoStore.grammarItems" :key="index" class="bg-learning-bg-primary rounded-xl p-4 border border-learning-bg-tertiary">
              <h4 class="font-medium text-learning-text-primary mb-2 flex items-center gap-2 flex-wrap">
                <span class="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded">Pattern {{ index + 1 }}</span>
                <code class="text-sm bg-learning-bg-secondary px-2 py-0.5 rounded">{{ grammar.pattern }}</code>
                <span v-if="grammar.pattern_zh" class="text-sm text-learning-chinese">{{ grammar.pattern_zh }}</span>
              </h4>
              <p class="text-sm text-learning-text-secondary mb-1">{{ grammar.explanation }}</p>
              <p v-if="grammar.explanation_zh" class="text-sm text-learning-chinese mb-3">{{ grammar.explanation_zh }}</p>
              <div class="space-y-1">
                <p class="text-xs font-medium text-learning-text-muted uppercase tracking-wide">{{ t('Examples', '例句') }}:</p>
                <ul class="space-y-1">
                  <li v-for="(example, exIndex) in grammar.examples" :key="exIndex" class="text-sm text-learning-text-secondary pl-3 border-l-2 border-learning-accent-primary/30">
                    {{ example }}
                    <span v-if="grammar.examples_zh && grammar.examples_zh[exIndex]" class="text-learning-chinese text-xs ml-1">
                      {{ grammar.examples_zh[exIndex] }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <p v-if="videoStore.grammarItems.length === 0" class="text-center text-learning-text-muted py-8">
            No grammar notes available for this video.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>