<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useVideoStore } from '@/stores';
import { videoService } from '@/services/video.service';
import VideoPlayer from '@/components/video/VideoPlayer.vue';
import StudyPlanDisplay from '@/components/learning/StudyPlanDisplay.vue';
import VocabularyCard from '@/components/learning/VocabularyCard.vue';
import ShadowingMode from '@/components/learning/ShadowingMode.vue';
import type { TranscriptSegment } from '@/types';

const route = useRoute();
const videoStore = useVideoStore();

const videoId = computed(() => route.params.id as string);

const showShadowingMode = ref(false);
const showVocabularyReview = ref(false);
const showGrammarNotes = ref(false);
const showZh = ref(true);
const videoRef = ref<InstanceType<typeof VideoPlayer> | null>(null);
const currentTime = ref(0);
const isLoading = ref(false);
const error = ref<string | null>(null);
const videoSrc = ref('');
const videoStatus = ref<'idle' | 'loading' | 'ready' | 'error'>('idle');

function toggleZh() {
  showZh.value = !showZh.value;
}

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

const shadowingSentences = computed(() =>
  currentTranscriptSegments.value.map((seg, index) => ({
    id: `sentence-${index}`,
    text: seg.text,
    startTime: seg.start,
    endTime: seg.end,
    translation: seg.text,
  }))
);

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
    <header class="sticky top-0 z-40 bg-learning-bg-secondary border-b border-learning-bg-tertiary">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link to="/" class="text-xl font-bold font-display text-learning-text-primary">
            Speak
          </router-link>
          <span class="text-learning-text-muted">/</span>
          <span class="text-learning-text-secondary">Learning / 學習</span>
        </div>
        <div class="flex items-center gap-4">
          <button
            @click="toggleZh"
            class="px-3 py-1.5 text-sm rounded border transition-colors"
            :class="showZh
              ? 'bg-learning-accent-primary text-white border-learning-accent-primary'
              : 'bg-learning-bg-primary text-learning-text-secondary border-learning-bg-tertiary hover:border-learning-accent-primary'"
          >
            中文
          </button>
          <router-link
            to="/"
            class="text-sm text-learning-text-secondary hover:text-learning-text-primary transition-colors"
          >
            Back to Dashboard / 返回主頁
          </router-link>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-6">
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full mr-4"></div>
        <span class="text-learning-text-secondary">Loading video... / 載入中...</span>
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
                :show-zh="showZh"
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
                  Chunks / 片段
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
                    : 'bg-learning-bg-primary text-learning-text-secondary hover:bg-learning-bg-secondary'"
                >
                  <span class="block">{{ index + 1 }}</span>
                  <span class="block text-xs opacity-70 font-mono">{{ Math.floor(chunk.start_time / 60).toString().padStart(2, '0') }}:{{ Math.floor(chunk.start_time % 60).toString().padStart(2, '0') }}</span>
                </button>
              </div>
            </div>

            <div v-if="!showShadowingMode" class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  :show-zh="showZh"
                  @play-audio="handleVocabularyPlay"
                  @save-word="handleVocabularySave"
                />
              </div>
            </div>

            <div v-if="showShadowingMode" class="card-interactive">
              <ShadowingMode
                :sentences="shadowingSentences"
                :is-active="showShadowingMode"
                @sentence-complete="handleSentenceComplete"
                @practice-complete="handlePracticeComplete"
              />
            </div>
          </div>

          <div class="space-y-6">
            <StudyPlanDisplay
              v-if="studyPlanProps"
              :plan="studyPlanProps.plan"
              :current-chunk-index="studyPlanProps.currentChunkIndex"
              :show-zh="showZh"
              @start-learning="handleStartLearning"
              @toggle-objective="handleToggleObjective"
              @select-objective="handleSelectObjective"
            />

            <div v-else class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
                Study Plan / 學習計劃
              </h3>
              <p class="text-learning-text-secondary text-sm">
                No study plan available for this video yet. / 此影片尚無學習計劃。
              </p>
            </div>

            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
                Quick Actions / 快速操作
              </h3>
              <div class="space-y-3">
                <button
                  @click="showShadowingMode = !showShadowingMode"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary hover:bg-learning-bg-secondary rounded-lg transition-colors text-left"
                >
                  <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-learning-text-primary">Shadowing Mode / 跟讀模式</p>
                    <p class="text-sm text-learning-text-secondary">Practice speaking / 練習口說</p>
                  </div>
                </button>

                <button
                  @click="showVocabularyReview = true"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary hover:bg-learning-bg-secondary rounded-lg transition-colors text-left"
                >
                  <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-learning-text-primary">Review Vocabulary / 複習詞匯</p>
                    <p class="text-sm text-learning-text-secondary">{{ videoStore.savedVocabulary.size }} saved / 已收藏</p>
                  </div>
                </button>

                <button
                  @click="showGrammarNotes = true"
                  class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary hover:bg-learning-bg-secondary rounded-lg transition-colors text-left"
                >
                  <div class="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-learning-text-primary">Grammar Notes / 文法筆記</p>
                    <p class="text-sm text-learning-text-secondary">{{ videoStore.grammarItems.length }} patterns / 句型</p>
                  </div>
                </button>
              </div>
            </div>

            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
                Progress / 進度
              </h3>
              <div class="space-y-4">
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-learning-text-secondary">Vocabulary learned / 詞匯已學</span>
                    <span class="text-learning-text-primary">{{ videoStore.savedVocabulary.size }} / {{ videoStore.vocabularyItems.length }}</span>
                  </div>
                  <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                    <div
                      class="h-full bg-learning-accent-secondary rounded-full"
                      :style="{ width: `${videoStore.vocabularyItems.length > 0 ? (videoStore.savedVocabulary.size / videoStore.vocabularyItems.length) * 100 : 0}%` }"
                    />
                  </div>
                </div>
                <div>
                  <div class="flex justify-between text-sm mb-2">
                    <span class="text-learning-text-secondary">Shadowing practice / 跟讀練習</span>
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
                    <span class="text-learning-text-secondary">Grammar patterns / 文法句型</span>
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
          <h3 class="text-xl font-semibold font-display text-learning-text-primary">Vocabulary Review / 詞匯複習</h3>
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
                @play-audio="handleVocabularyPlay"
                @save-word="handleVocabularySave"
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
          <h3 class="text-xl font-semibold font-display text-learning-text-primary">Grammar Notes / 文法筆記</h3>
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
                <span v-if="grammar.pattern_zh" class="text-sm text-purple-400">{{ grammar.pattern_zh }}</span>
              </h4>
              <p class="text-sm text-learning-text-secondary mb-1">{{ grammar.explanation }}</p>
              <p v-if="grammar.explanation_zh" class="text-sm text-learning-accent-secondary mb-3">{{ grammar.explanation_zh }}</p>
              <div class="space-y-1">
                <p class="text-xs font-medium text-learning-text-muted uppercase tracking-wide">Examples / 例句:</p>
                <ul class="space-y-1">
                  <li v-for="(example, exIndex) in grammar.examples" :key="exIndex" class="text-sm text-learning-text-secondary pl-3 border-l-2 border-learning-accent-primary/30">
                    {{ example }}
                    <span v-if="grammar.examples_zh && grammar.examples_zh[exIndex]" class="text-purple-400 text-xs ml-1">
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