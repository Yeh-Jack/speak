import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Video, VideoChunk, Transcript, StudyPlan } from '@/types';

export const useVideoStore = defineStore('video', () => {
  const currentVideo = ref<Video | null>(null);
  const chunks = ref<VideoChunk[]>([]);
  const currentChunkIndex = ref(0);
  const transcripts = ref<Record<string, Transcript>>({});
  const studyPlans = ref<Record<number, StudyPlan>>({});
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const savedVocabulary = ref<Set<string>>(new Set());

  const currentChunk = computed(() => chunks.value[currentChunkIndex.value] || null);

  const currentTranscript = computed(() => {
    const priorityOrder = ['user', 'youtube_author', 'whisper', 'youtube_auto'];
    for (const type of priorityOrder) {
      if (transcripts.value[type]) {
        return transcripts.value[type];
      }
    }
    return null;
  });

  const currentStudyPlan = computed(() => studyPlans.value[currentChunkIndex.value] || null);

  const currentTranscriptSegments = computed(() => {
    return currentTranscript.value?.segments || [];
  });

  const vocabularyItems = computed(() => {
    return currentStudyPlan.value?.vocabulary || [];
  });

  function setVideo(video: Video) {
    currentVideo.value = video;
  }

  function setChunks(newChunks: VideoChunk[]) {
    chunks.value = newChunks;
  }

  function setCurrentChunkIndex(index: number) {
    if (index >= 0 && index < chunks.value.length) {
      currentChunkIndex.value = index;
    }
  }

  function nextChunk() {
    if (currentChunkIndex.value < chunks.value.length - 1) {
      currentChunkIndex.value++;
    }
  }

  function previousChunk() {
    if (currentChunkIndex.value > 0) {
      currentChunkIndex.value--;
    }
  }

  function setTranscript(type: string, transcript: Transcript) {
    transcripts.value[type] = transcript;
  }

  function setStudyPlan(chunkIndex: number, plan: StudyPlan) {
    studyPlans.value[chunkIndex] = plan;
  }

  function toggleVocabularySave(word: string) {
    if (savedVocabulary.value.has(word)) {
      savedVocabulary.value.delete(word);
    } else {
      savedVocabulary.value.add(word);
    }
  }

  function isVocabularySaved(word: string): boolean {
    return savedVocabulary.value.has(word);
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading;
  }

  function setError(err: string | null) {
    error.value = err;
  }

  function reset() {
    currentVideo.value = null;
    chunks.value = [];
    currentChunkIndex.value = 0;
    transcripts.value = {};
    studyPlans.value = {};
    isLoading.value = false;
    error.value = null;
  }

  return {
    currentVideo,
    chunks,
    currentChunkIndex,
    currentChunk,
    transcripts,
    studyPlans,
    currentTranscript,
    currentStudyPlan,
    currentTranscriptSegments,
    vocabularyItems,
    isLoading,
    error,
    savedVocabulary,
    setVideo,
    setChunks,
    setCurrentChunkIndex,
    nextChunk,
    previousChunk,
    setTranscript,
    setStudyPlan,
    toggleVocabularySave,
    isVocabularySaved,
    setLoading,
    setError,
    reset,
  };
});