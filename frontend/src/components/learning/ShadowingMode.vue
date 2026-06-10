<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import BaseButton from '@/components/common/BaseButton.vue';
import { useI18n } from '@/composables/useI18n';
import { useVideoStore, useLanguageStore } from '@/stores';
import videoService from '@/services/video.service';
import api from '@/services/api';

const { t } = useI18n();
const videoStore = useVideoStore();
const languageStore = useLanguageStore();

export interface ShadowingSentence {
  id: string;
  text: string;
  startTime: number;
  endTime: number;
  translation?: string;
  chunkIndex: number;
}

interface Props {
  sentences: ShadowingSentence[];
  videoId: string;
  isActive?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false,
});

const emit = defineEmits<{
  sentenceComplete: [sentenceId: string];
  practiceComplete: [];
  close: [];
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
const recordingError = ref<string>('');
const micVolume = ref(1.0);
const speakerVolume = ref(1.0);
const recordingScore = ref<{ score: number; feedback_en: string; feedback_zh: string; originalText: string; userText: string } | null>(null);
const isScoring = ref(false);
const recordingCountdown = ref(0);
let lastScoredBlob: Blob | null = null;

let mediaRecorder: MediaRecorder | null = null;
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let animationFrame: number | null = null;
let speechRecognition: any = null;
let currentAudio: HTMLAudioElement | null = null;
let stopInterval: ReturnType<typeof setInterval> | null = null;
let intervalStarted = false;

const currentSentence = computed(() => props.sentences[currentSentenceIndex.value]);

const progress = computed(() => {
  if (props.sentences.length === 0) return 0;
  return ((currentSentenceIndex.value + 1) / props.sentences.length) * 100;
});

const allCompleted = computed(() => {
  return props.sentences.every((s) => userScore.value[s.id] !== undefined);
});

const scoreFeedback = computed(() => {
  if (!recordingScore.value) return { en: '', zh: '' };
  const en = recordingScore.value.feedback_en || '';
  const zh = recordingScore.value.feedback_zh || '';
  if (languageStore.showZh) {
    return { en, zh };
  }
  return { en, zh: '' };
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
  recordingError.value = '';

  // Clear old recording data for retry
  recordedBlob.value = null;
  recordingScore.value = null;
  lastScoredBlob = null;

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    recordingError.value = t('Recording not supported in this browser', '此瀏覽器不支援錄音');
    return;
  }

  const isSecure = location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
  if (!isSecure) {
    console.warn('[Shadowing] Recording requires HTTPS');
  }

  // Pre-request microphone BEFORE countdown (eliminates delay)
  let stream: MediaStream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
      },
    });
  } catch (err) {
    recordingError.value = t('Microphone access denied', '麥克風訪問被拒絕');
    return;
  }

  // Start countdown with stream already available
  recordingCountdown.value = 3;

  const countdownInterval = setInterval(() => {
    recordingCountdown.value--;
    if (recordingCountdown.value <= 0) {
      clearInterval(countdownInterval);
      beginRecording(stream);
    }
  }, 1000);
}

function beginRecording(stream: MediaStream) {
  recordingCountdown.value = 0;
  showWaveform.value = true;
  isRecording.value = true;

  audioContext = new AudioContext();
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;

  const source = audioContext.createMediaStreamSource(stream);

  const gainNode = audioContext.createGain();
  gainNode.gain.value = micVolume.value;
  source.connect(gainNode);
  gainNode.connect(analyser);

  const destStream = audioContext.createMediaStreamDestination();
  gainNode.connect(destStream);

  const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
    ? 'audio/webm;codecs=opus'
    : MediaRecorder.isTypeSupported('audio/webm')
      ? 'audio/webm'
      : 'audio/ogg';

  mediaRecorder = new MediaRecorder(destStream.stream, { mimeType });
  const chunks: Blob[] = [];

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      chunks.push(e.data);
    }
  };

  mediaRecorder.onstop = () => {
    if (chunks.length === 0) {
      recordedBlob.value = null;
      return;
    }
    recordedBlob.value = new Blob(chunks, { type: mimeType });
    stream.getTracks().forEach((track) => track.stop());

    // Auto-score after recording stops
    scoreRecording();
  };

  mediaRecorder.onerror = (e) => {
    console.error('[Shadowing] MediaRecorder error:', e);
  };

  mediaRecorder.start(100);

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
}

function stopRecording() {
  console.log('[Shadowing] stopRecording called, current state:', {
    hasMediaRecorder: !!mediaRecorder,
    isRecording: isRecording.value,
    recorderState: mediaRecorder?.state,
  });

  if (mediaRecorder && isRecording.value) {
    console.log('[Shadowing] Stopping MediaRecorder...');
    mediaRecorder.stop();
    isRecording.value = false;
    showWaveform.value = false;
    audioLevel.value = 0;
    console.log('[Shadowing] MediaRecorder stopped');

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

  stopCurrentAudio();
  isPlayingPractice.value = true;

  const sentence = currentSentence.value;
  const chunk = videoStore.chunks[sentence.chunkIndex];

  if (!chunk) {
    console.error('[Shadowing] Chunk not found for index:', sentence.chunkIndex);
    fallbackToTTS(sentence.text);
    return;
  }

  try {
    const audioUrl = await videoService.getAudioUrl(props.videoId, sentence.chunkIndex);

    const audio = new Audio(audioUrl);
    currentAudio = audio;
    audio.playbackRate = 0.8;

    const startOffset = Math.max(0, sentence.startTime - chunk.start_time);
    const targetEndOffset = sentence.endTime - chunk.start_time;

    audio.onloadedmetadata = () => {
      if (currentAudio !== audio) return;

      const audioDuration = audio.duration;
      if (!isFinite(audioDuration) || audioDuration <= 0) {
        console.error('[Shadowing] Invalid audio duration:', audioDuration);
        if (currentAudio === audio) {
          currentAudio = null;
          fallbackToTTS(sentence.text);
        }
        return;
      }

      const endOffset = Math.min(audioDuration, targetEndOffset);

      if (endOffset <= startOffset) {
        console.error('[Shadowing] Invalid offset range:', { startOffset, endOffset });
        if (currentAudio === audio) {
          currentAudio = null;
          fallbackToTTS(sentence.text);
        }
        return;
      }

      const onceHandler = () => {
        if (currentAudio !== audio) return;

        console.log('[Shadowing] Setting currentTime to', startOffset);
        audio.currentTime = startOffset;

        audio.onplaying = () => {
          if (currentAudio !== audio || intervalStarted) return;

          intervalStarted = true;
          if (stopInterval) clearInterval(stopInterval);

          stopInterval = setInterval(() => {
            if (currentAudio !== audio) {
              if (stopInterval) {
                clearInterval(stopInterval);
                stopInterval = null;
              }
              intervalStarted = false;
              return;
            }

            if (audio.currentTime >= endOffset) {
              if (stopInterval) {
                clearInterval(stopInterval);
                stopInterval = null;
              }
              intervalStarted = false;
              audio.pause();
              audio.dispatchEvent(new Event('ended'));
            }
          }, 100);
        };

        audio.onended = () => {
          if (stopInterval) {
            clearInterval(stopInterval);
            stopInterval = null;
          }
          intervalStarted = false;
          if (currentAudio === audio) {
            isPlayingPractice.value = false;
            currentAudio = null;
          }
          URL.revokeObjectURL(audio.src);
        };

        audio.onerror = (e) => {
          console.error('[Shadowing] Audio playback error:', e);
          if (stopInterval) {
            clearInterval(stopInterval);
            stopInterval = null;
          }
          intervalStarted = false;
          if (currentAudio === audio) {
            currentAudio = null;
            fallbackToTTS(sentence.text);
          }
        };

        audio.play().catch((err) => {
          console.error('[Shadowing] Play promise rejected:', err);
          if (currentAudio === audio) {
            currentAudio = null;
            fallbackToTTS(sentence.text);
          }
        });
      };

      audio.addEventListener('canplay', onceHandler, { once: true });
    };

    audio.onerror = (e) => {
      console.error('[Shadowing] Audio load error:', e);
      if (currentAudio === audio) {
        currentAudio = null;
        fallbackToTTS(sentence.text);
      }
    };

    audio.load();
  } catch (err) {
    console.error('[Shadowing] playOriginal error:', err);
    currentAudio = null;
    isPlayingPractice.value = false;
    fallbackToTTS(sentence.text);
  }
}

function stopCurrentAudio() {
  if (stopInterval) {
    clearInterval(stopInterval);
    stopInterval = null;
  }
  intervalStarted = false;
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.onended = null;
    currentAudio.ontimeupdate = null;
    currentAudio.onloadedmetadata = null;
    currentAudio.oncanplay = null;
    currentAudio.onplaying = null;
    currentAudio.onerror = null;
    currentAudio = null;
  }
}

function fallbackToTTS(text: string) {
  isPlayingPractice.value = false;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';
  utterance.rate = 0.8;

  utterance.onend = () => {
    isPlayingPractice.value = false;
  };

  utterance.onerror = () => {
    isPlayingPractice.value = false;
  };

  speechSynthesis.speak(utterance);
}

async function scoreRecording() {
  if (!recordedBlob.value || !currentSentence.value) return;
  if (recordedBlob.value === lastScoredBlob) return;

  isScoring.value = true;
  recordingScore.value = null;

  try {
    const formData = new FormData();
    formData.append('file', recordedBlob.value, 'recording.webm');

    const response = await api.post(
      `/speaking/videos/${props.videoId}/compare?start=${currentSentence.value.startTime}&end=${currentSentence.value.endTime}&language=en`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    lastScoredBlob = recordedBlob.value;
    recordingScore.value = {
      score: response.data.similarity_score,
      feedback_en: response.data.feedback_en,
      feedback_zh: response.data.feedback_zh,
      originalText: response.data.original_text,
      userText: response.data.user_text,
    };
  } catch (err: any) {
    console.error('[Shadowing] Scoring failed:', err);
  } finally {
    isScoring.value = false;
  }
}

function playRecording() {
  if (!recordedBlob.value) return;

  const url = URL.createObjectURL(recordedBlob.value);

  const audio = new Audio(url);
  audio.volume = speakerVolume.value;

  audio.onended = () => {
    URL.revokeObjectURL(url);
  };

  audio.onerror = (e) => {
    console.error('[Shadowing] Recording playback error:', e);
    URL.revokeObjectURL(url);
  };

  audio.play().catch((err) => {
    console.error('[Shadowing] Recording playback failed:', err);
    URL.revokeObjectURL(url);
  });
}

function nextSentence() {
  stopCurrentAudio();
  lastScoredBlob = null;
  recordingScore.value = null;
  if (currentSentenceIndex.value < props.sentences.length - 1) {
    currentSentenceIndex.value++;
    recordedBlob.value = null;
    recognizedText.value = '';
  } else {
    emit('practiceComplete');
  }
}

function previousSentence() {
  stopCurrentAudio();
  lastScoredBlob = null;
  recordingScore.value = null;
  if (currentSentenceIndex.value > 0) {
    currentSentenceIndex.value--;
    recordedBlob.value = null;
    recognizedText.value = '';
  }
}

function restartPractice() {
  stopCurrentAudio();
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
    stopCurrentAudio();
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
  stopCurrentAudio();
});
</script>

<template>
  <div class="bg-learning-bg-expanded rounded-xl border border-learning-bg-tertiary overflow-hidden">
    <div class="p-5 border-b border-learning-bg-tertiary">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold font-display text-learning-text-primary flex items-center gap-2">
          <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          {{ t('Shadowing Practice', '跟讀練習') }}
        </h2>
        <div class="flex items-center gap-3">
          <span class="text-sm text-learning-text-secondary">
            {{ currentSentenceIndex + 1 }} / {{ sentences.length }}
          </span>
          <button
            @click="emit('close')"
            class="p-1 rounded hover:bg-learning-bg-primary transition-colors"
          >
            <svg class="w-5 h-5 text-learning-text-muted hover:text-learning-text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
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

        <div v-if="recordingError" class="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p class="text-red-400 text-sm text-center">{{ recordingError }}</p>
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
            :disabled="currentSentenceIndex >= sentences.length - 1"
            class="p-2 rounded-lg transition-colors disabled:opacity-50"
            :class="currentSentenceIndex >= sentences.length - 1 ? 'text-gray-600' : 'text-learning-text-secondary hover:bg-learning-bg-primary'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div
          v-if="recordingCountdown > 0"
          class="flex flex-col items-center justify-center py-4"
        >
          <div class="text-5xl font-bold text-learning-accent-primary animate-pulse">
            {{ recordingCountdown }}
          </div>
          <div class="text-sm text-learning-text-secondary mt-2">
            {{ languageStore.showZh ? '準備說...' : 'Get ready...' }}
          </div>
        </div>

        <div class="flex items-center justify-center gap-6 my-4">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-learning-text-secondary" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
            <span class="text-xs text-learning-text-secondary">{{ t('Mic', '麥克風') }}</span>
            <input
              v-model="micVolume"
              type="range"
              min="0"
              max="2"
              step="0.1"
              class="w-20 h-1.5 bg-learning-bg-tertiary rounded-lg appearance-none cursor-pointer accent-learning-accent-primary"
            />
            <span class="text-xs text-learning-text-muted w-8">{{ Math.round(micVolume * 100) }}%</span>
          </div>

          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-learning-text-secondary" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
            </svg>
            <span class="text-xs text-learning-text-secondary">{{ t('Speaker', '喇叭') }}</span>
            <input
              v-model="speakerVolume"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-20 h-1.5 bg-learning-bg-tertiary rounded-lg appearance-none cursor-pointer accent-learning-accent-primary"
            />
            <span class="text-xs text-learning-text-muted w-8">{{ Math.round(speakerVolume * 100) }}%</span>
          </div>
        </div>

        <div class="flex items-center justify-center gap-4">
          <button
            v-spray
            @click="playOriginal"
            class="flex items-center gap-2 px-4 py-2 bg-learning-bg-primary text-learning-text-primary rounded-lg transition-colors"
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

        <!-- Dedicated Score Area -->
        <div
          v-if="isScoring || recordingScore"
          class="mt-4 px-4 py-3 bg-learning-bg-primary rounded-lg"
        >
          <div v-if="isScoring" class="flex items-center justify-center gap-3">
            <svg class="w-5 h-5 animate-spin text-learning-accent-secondary" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <span class="text-sm text-learning-text-secondary">{{ t('Scoring...', '評分中...') }}</span>
          </div>
          <div v-else-if="recordingScore" class="flex flex-col gap-2">
            <div class="flex items-center gap-3">
              <span class="text-2xl font-bold" :class="{
                'text-green-400': recordingScore.score >= 80,
                'text-yellow-400': recordingScore.score >= 60 && recordingScore.score < 80,
                'text-red-400': recordingScore.score < 60
              }">
                {{ Math.round(recordingScore.score * 100) }}%
              </span>
              <div class="flex flex-col gap-1">
              <span v-if="scoreFeedback.en" class="text-sm text-learning-text-secondary">{{ scoreFeedback.en }}</span>
              <span v-if="languageStore.showZh && scoreFeedback.zh" class="text-sm text-learning-chinese">{{ scoreFeedback.zh }}</span>
            </div>
            </div>
            <div class="text-xs text-learning-text-muted">
              <span class="text-learning-text-secondary">{{ t('Recognized:', '識別內容：') }}</span> <span class="text-learning-chinese">{{ recordingScore.userText }}</span>
            </div>
          </div>
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