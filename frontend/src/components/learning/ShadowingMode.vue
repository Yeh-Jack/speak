<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import BaseButton from '@/components/common/BaseButton.vue';
import { useI18n } from '@/composables/useI18n';

const { t } = useI18n();

export interface ShadowingSentence {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  translation?: string;
}

interface Props {
  sentences: ShadowingSentence[];
  isActive?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
});

const emit = defineEmits<{
  sentenceComplete: [sentenceId: string];
  practiceComplete: [];
}>();

const isRecording = ref(false);
const isRecognizing = ref(false);
const currentSentenceIndex = ref(0);
const recordedBlob = ref<Blob | null>(null);
const audioLevel = ref(0);
const showWaveform = ref(false);
const isPlayingPractice = ref(false);
const userScore = ref<Record<string, number>>({});
const recognizedText = ref<string>('');
const waveformBars = ref<number[]>(new Array(32).fill(8));

let mediaRecorder: MediaRecorder | null = null;
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let animationFrame: number | null = null;
let speechRecognition: any = null;

const currentSentence = computed(() => props.sentences[currentSentenceIndex.value]);

const progress = computed(() => {
  if (props.sentences.length === 0) return 0;
  return ((currentSentenceIndex.value + 1) / props.sentences.length) * 100;
});

const allCompleted = computed(() => {
  return props.sentences.every((s) => userScore.value[s.id] !== undefined);
});

function initSpeechRecognition() {
  if (typeof window === 'undefined') return null;
  
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) return null;

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';
  
  recognition.onresult = (event: any) => {
    let finalTranscript = '';
    let interimTranscript = '';
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }
    
    recognizedText.value = finalTranscript || interimTranscript;
  };

  recognition.onerror = (event: any) => {
    console.error('Speech recognition error:', event.error);
    isRecognizing.value = false;
  };

  recognition.onend = () => {
    isRecognizing.value = false;
    if (recognizedText.value && currentSentence.value) {
      const score = calculateSimilarity(recognizedText.value, currentSentence.value.text);
      userScore.value[currentSentence.value.id] = score;
      emit('sentenceComplete', currentSentence.value.id);
    }
  };

  return recognition;
}

function calculateSimilarity(str1: string, str2: string): number {
  const s1 = str1.toLowerCase().trim();
  const s2 = str2.toLowerCase().trim();
  
  if (s1 === s2) return 100;
  if (s1.length === 0 || s2.length === 0) return 0;

  const words1 = s1.split(/\s+/);
  const words2 = s2.split(/\s+/);
  
  const matchedWords = words1.filter(word => words2.some(w => w.includes(word) || word.includes(w)));
  const similarity = (matchedWords.length * 2) / (words1.length + words2.length);
  
  const lengthPenalty = Math.min(s1.length, s2.length) / Math.max(s1.length, s2.length);
  
  return Math.round((similarity * 0.7 + lengthPenalty * 0.3) * 100);
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    mediaRecorder = new MediaRecorder(stream);
    const chunks: Blob[] = [];

    mediaRecorder.ondataavailable = (e) => {
      chunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      recordedBlob.value = new Blob(chunks, { type: 'audio/webm' });
      stream.getTracks().forEach((track) => track.stop());
    };

    mediaRecorder.start();
    isRecording.value = true;
    showWaveform.value = true;

    if (!speechRecognition) {
      speechRecognition = initSpeechRecognition();
    }

    if (speechRecognition) {
      recognizedText.value = '';
      speechRecognition.start();
      isRecognizing.value = true;
    }

    function updateWaveform() {
      if (!analyser || !isRecording.value) return;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(dataArray);

      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      audioLevel.value = Math.min(average / 128, 1);

      const bars = [];
      for (let i = 0; i < 32; i++) {
        const value = dataArray[i] || 0;
        bars.push(Math.max(8, (value / 255) * 64));
      }
      waveformBars.value = bars;

      animationFrame = requestAnimationFrame(updateWaveform);
    }

    updateWaveform();
  } catch (error) {
    console.error('Failed to start recording:', error);
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop();
    isRecording.value = false;
    showWaveform.value = false;
    audioLevel.value = 0;

    if (animationFrame) {
      cancelAnimationFrame(animationFrame);
    }

    if (audioContext) {
      audioContext.close();
      audioContext = null;
    }

    if (speechRecognition && isRecognizing.value) {
      speechRecognition.stop();
    }

    if (!userScore.value[currentSentence.value?.id || '']) {
      userScore.value[currentSentence.value?.id || ''] = 0;
    }
  }
}

async function playOriginal() {
  if (!currentSentence.value) return;

  const utterance = new SpeechSynthesisUtterance(currentSentence.value.text);
  utterance.lang = 'en-US';
  utterance.rate = 0.8;

  isPlayingPractice.value = true;
  utterance.onend = () => {
    isPlayingPractice.value = false;
  };

  speechSynthesis.speak(utterance);
}

function playRecording() {
  if (!recordedBlob.value) return;

  const url = URL.createObjectURL(recordedBlob.value);
  const audio = new Audio(url);
  audio.play();

  audio.onended = () => {
    URL.revokeObjectURL(url);
  };
}

function nextSentence() {
  if (currentSentenceIndex.value < props.sentences.length - 1) {
    currentSentenceIndex.value++;
    recordedBlob.value = null;
    recognizedText.value = '';
  } else {
    emit('practiceComplete');
  }
}

function previousSentence() {
  if (currentSentenceIndex.value > 0) {
    currentSentenceIndex.value--;
    recordedBlob.value = null;
    recognizedText.value = '';
  }
}

function restartPractice() {
  currentSentenceIndex.value = 0;
  recordedBlob.value = null;
  userScore.value = {};
  recognizedText.value = '';
}

watch(() => props.isActive, (active) => {
  if (!active) {
    isRecording.value = false;
    showWaveform.value = false;
    recordedBlob.value = null;
    if (speechRecognition && isRecognizing.value) {
      speechRecognition.stop();
    }
  }
});

onUnmounted(() => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop();
  }
  if (audioContext) {
    audioContext.close();
  }
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
  if (speechRecognition && isRecognizing.value) {
    speechRecognition.stop();
  }
  speechSynthesis.cancel();
});
</script>

<template>
  <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary overflow-hidden">
    <div class="p-5 border-b border-learning-bg-tertiary">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold font-display text-learning-text-primary flex items-center gap-2">
          <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          {{ t('Shadowing Practice', '跟讀練習') }}
        </h2>
        <span class="text-sm text-learning-text-secondary">
          {{ currentSentenceIndex + 1 }} / {{ sentences.length }}
        </span>
      </div>

      <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
        <div
          class="h-full bg-gradient-to-r from-learning-accent-primary to-learning-accent-secondary rounded-full transition-all duration-300"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>

    <div class="p-5">
      <div v-if="currentSentence" class="mb-6">
        <div class="text-center mb-6">
          <p class="text-2xl font-bold text-learning-text-primary mb-3 font-display">
            "{{ currentSentence.text }}"
          </p>
          <p v-if="currentSentence.translation" class="text-learning-text-secondary">
            {{ currentSentence.translation }}
          </p>
        </div>

        <div
          v-if="showWaveform"
          class="flex items-center justify-center gap-1 h-16 mb-4"
        >
          <div
            v-for="(height, i) in waveformBars"
            :key="i"
            class="w-1 bg-learning-accent-secondary rounded-full transition-all duration-75"
            :style="{
              height: `${height}px`,
              opacity: audioLevel > 0.1 ? 1 : 0.3
            }"
          />
        </div>

        <div class="flex items-center justify-center gap-3 mb-4">
          <button
            @click="previousSentence"
            :disabled="currentSentenceIndex === 0"
            class="p-2 rounded-lg transition-colors disabled:opacity-50"
            :class="currentSentenceIndex === 0 ? 'text-gray-600' : 'text-learning-text-secondary hover:bg-learning-bg-primary'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <button
            v-if="!isRecording"
            @click="startRecording"
            class="w-16 h-16 rounded-full bg-learning-accent-primary hover:bg-learning-accent-primary/90 flex items-center justify-center transition-all transform hover:scale-105 glow-accent"
          >
            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          </button>

          <button
            v-else
            @click="stopRecording"
            class="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center transition-all transform hover:scale-105 animate-pulse-subtle"
          >
            <div class="w-6 h-6 bg-white rounded-full" />
          </button>

          <button
            @click="nextSentence"
            :disabled="!recordedBlob && !userScore[currentSentence.id]"
            class="p-2 rounded-lg transition-colors disabled:opacity-50"
            :class="!recordedBlob && !userScore[currentSentence.id] ? 'text-gray-600' : 'text-learning-text-secondary hover:bg-learning-bg-primary'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div class="flex items-center justify-center gap-4">
          <button
            @click="playOriginal"
            class="flex items-center gap-2 px-4 py-2 bg-learning-bg-primary hover:bg-learning-bg-secondary text-learning-text-primary rounded-lg transition-colors"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
            </svg>
            <span class="text-sm">{{ t('Original', '原始') }}</span>
          </button>

          <button
            v-if="recordedBlob"
            @click="playRecording"
            class="flex items-center gap-2 px-4 py-2 bg-learning-accent-secondary/10 hover:bg-learning-accent-secondary/20 text-learning-accent-secondary rounded-lg transition-colors"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <span class="text-sm">{{ t('Playback', '播放') }}</span>
          </button>

          <span
            v-if="userScore[currentSentence.id]"
            class="flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium"
            :class="{
              'bg-green-500/20 text-green-400': userScore[currentSentence.id] >= 90,
              'bg-yellow-500/20 text-yellow-400': userScore[currentSentence.id] >= 70 && userScore[currentSentence.id] < 90,
              'bg-red-500/20 text-red-400': userScore[currentSentence.id] < 70
            }"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
            {{ userScore[currentSentence.id] }}%
          </span>
        </div>
      </div>

      <div v-else class="text-center py-8">
        <p class="text-learning-text-muted mb-4">{{ t('No sentences available for shadowing', '尚無可用於跟讀的句子') }}</p>
      </div>

      <div v-if="allCompleted" class="mt-6 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
        <div class="flex items-center justify-center gap-3">
          <svg class="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
          <span class="text-green-400 font-medium">{{ t('Practice Complete!', '練習完成！') }}</span>
        </div>
        <div class="flex justify-center mt-4 gap-2">
          <BaseButton variant="secondary" @click="restartPractice">
            {{ t('Practice Again', '再次練習') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>