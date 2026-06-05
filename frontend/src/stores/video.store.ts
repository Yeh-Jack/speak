import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Video, VideoChunk, Transcript } from '@/types';
import type { StudyPlanResponse } from '@/services/video.service';

export const useVideoStore = defineStore('video', () => {
  const currentVideo = ref<Video | null>(null);
  const chunks = ref<VideoChunk[]>([]);
  const currentChunkIndex = ref(0);
  const transcripts = ref<Record<string, Transcript>>({});
  const studyPlans = ref<StudyPlanResponse | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const savedVocabulary = ref<Set<string>>(new Set());

  const isCreatingVideo = ref(false);
  const createProgress = ref('');
  const createdVideoId = ref<string | null>(null);
  const createError = ref<string | null>(null);

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

  const currentStudyPlan = computed(() => {
    console.log('currentStudyPlan computed, studyPlans.value:', !!studyPlans.value);
    return studyPlans.value;
  });

  const currentTranscriptSegments = computed(() => {
    return currentTranscript.value?.segments || [];
  });

  const vocabularyItems = computed(() => {
    return currentStudyPlan.value?.vocabulary || [];
  });

  const grammarItems = computed(() => {
    return currentStudyPlan.value?.grammar || [];
  });

  const studyObjectives = computed(() => {
    return currentStudyPlan.value?.objectives || [];
  });

  const totalChunks = computed(() => chunks.value.length);

  const completedObjectives = computed(() => {
    return studyObjectives.value.filter(obj => obj.completed).length;
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

  function setStudyPlan(plan: StudyPlanResponse) {
    console.log('setStudyPlan called with:', {
      hasPlan: !!plan,
      vocabularyCount: plan?.vocabulary?.length || 0,
      grammarCount: plan?.grammar?.length || 0,
      planId: plan?.id
    });
    studyPlans.value = plan;
  }

  function toggleObjective(objectiveId: string) {
    if (!studyPlans.value) return;
    const objectives = studyPlans.value.objectives.map(obj => {
      if (obj.id === objectiveId) {
        return { ...obj, completed: !obj.completed };
      }
      return obj;
    });
    studyPlans.value = { ...studyPlans.value, objectives };
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
    studyPlans.value = null;
    isLoading.value = false;
    error.value = null;
  }

  function setCreatingVideo(creating: boolean, progress: string = '', videoId: string | null = null, error: string | null = null) {
    isCreatingVideo.value = creating;
    createProgress.value = progress;
    createdVideoId.value = videoId;
    createError.value = error;
  }

  function updateCreateProgress(progress: string) {
    createProgress.value = progress;
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
    grammarItems,
    studyObjectives,
    totalChunks,
    completedObjectives,
    isLoading,
    error,
    savedVocabulary,
    isCreatingVideo,
    createProgress,
    createdVideoId,
    createError,
    setVideo,
    setChunks,
    setCurrentChunkIndex,
    nextChunk,
    previousChunk,
    setTranscript,
    setStudyPlan,
    toggleObjective,
    toggleVocabularySave,
    isVocabularySaved,
    setLoading,
    setError,
    reset,
    setCreatingVideo,
    updateCreateProgress,
  };
});