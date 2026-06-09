<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from '@/composables/useI18n';

const { t } = useI18n();

interface Props {
  word: string;
  wordZh?: string | null;
  definition?: string | null;
  definitionZh?: string | null;
  context?: string | null;
  contextZh?: string | null;
  cefrLevel?: string | null;
  cefrLevelZh?: string | null;
  pronunciation?: string;
  examples?: string[];
  examplesZh?: string[];
  isSaved?: boolean;
  showZh?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isSaved: false,
  showZh: true,
});

const emit = defineEmits<{
  playAudio: [word: string];
  saveWord: [word: string];
  markReviewed: [word: string];
}>();

const isFlipped = ref(false);
const isPlaying = ref(false);

const cefrColor = computed(() => {
  const colors: Record<string, string> = {
    A1: 'bg-green-500/20 text-green-400 border-green-500/30',
    A2: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    B1: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    B2: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    C1: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    C2: 'bg-red-500/20 text-red-400 border-red-500/30',
  };
  return colors[props.cefrLevel || ''] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
});

function flipCard() {
  isFlipped.value = !isFlipped.value;
}

async function playAudio() {
  if (isPlaying.value) return;
  isPlaying.value = true;
  emit('playAudio', props.word);

  const utterance = new SpeechSynthesisUtterance(props.word);
  utterance.lang = 'en-US';
  utterance.rate = 0.8;

  utterance.onend = () => {
    isPlaying.value = false;
  };

  utterance.onerror = () => {
    isPlaying.value = false;
  };

  speechSynthesis.speak(utterance);

  setTimeout(() => {
    isPlaying.value = false;
  }, 2000);
}

function saveWord() {
  emit('saveWord', props.word);
}
</script>

<template>
  <div
    class="relative h-[21rem] cursor-pointer perspective-1000"
    @click="flipCard"
  >
    <div
      class="relative w-full h-full transition-transform duration-500 transform-style-preserve-3d"
      :class="{ 'rotate-y-180': isFlipped }"
      style="transform-style: preserve-3d; transform: rotateY(0deg);"
      :style="{ transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)' }"
    >
      <div
        class="absolute inset-0 backface-hidden bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary shadow-card hover:shadow-card-hover transition-shadow"
        style="backface-visibility: hidden;"
      >
        <div class="flex flex-col h-full">
          <div class="flex items-start justify-between mb-3">
            <span
              v-if="cefrLevel"
              class="px-2 py-0.5 text-xs font-medium rounded border"
              :class="cefrColor"
            >
              {{ cefrLevel }}
            </span>
            <button
              @click.stop="saveWord"
              class="p-1.5 rounded-lg transition-colors"
              :class="isSaved ? 'text-learning-accent-primary' : 'text-gray-500 hover:text-gray-300'"
            >
              <svg
                class="w-5 h-5"
                :fill="isSaved ? 'currentColor' : 'none'"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
            </button>
          </div>

          <div class="flex-1 flex flex-col justify-center items-center text-center">
            <h3 class="text-2xl font-bold text-learning-text-primary mb-1 font-display">
              {{ word }}
            </h3>
            <p v-if="showZh && wordZh" class="text-lg text-learning-accent-secondary mb-2">
              {{ wordZh }}
            </p>
            <p v-if="pronunciation" class="text-sm text-learning-text-secondary mb-4">
              {{ pronunciation }}
            </p>
            <button
              @click.stop="playAudio"
              class="flex items-center gap-2 px-4 py-2 bg-learning-accent-secondary/10 hover:bg-learning-accent-secondary/20 text-learning-accent-secondary rounded-lg transition-colors"
              :class="{ 'animate-pulse-subtle': isPlaying }"
            >
              <svg class="w-4 h-4" :class="{ 'animate-bounce-gentle': isPlaying }" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
              </svg>
              <span class="text-sm font-medium">{{ t('Listen', '聽') }}</span>
            </button>
          </div>

          <p class="text-sm text-learning-text-muted text-center">{{ t('Click to flip', '點擊翻轉') }}</p>
        </div>
      </div>

      <div
        class="absolute inset-0 backface-hidden bg-learning-bg-tertiary rounded-xl p-5 border border-learning-accent-primary/30 shadow-card"
        style="backface-visibility: hidden; transform: rotateY(180deg);"
      >
        <div class="flex flex-col h-full">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-medium text-learning-accent-primary uppercase tracking-wide">
              {{ t('Definition', '定義') }}
            </span>
            <span
              v-if="cefrLevel"
              class="px-2 py-0.5 text-xs font-medium rounded border"
              :class="cefrColor"
            >
              {{ cefrLevel }}
            </span>
          </div>

          <div class="flex-1 overflow-auto">
            <p class="text-learning-text-primary leading-relaxed mb-2">
              {{ definition || 'No definition available' }}
            </p>
            <p v-if="showZh && definitionZh" class="text-learning-accent-secondary leading-relaxed mb-4">
              {{ definitionZh }}
            </p>

            <div v-if="context" class="mb-4">
              <p class="text-xs font-medium text-learning-text-secondary uppercase tracking-wide mb-1">
                {{ t('Context', '情境') }}
              </p>
              <p class="text-sm text-learning-text-muted italic">
                "{{ context }}"
              </p>
              <p v-if="showZh && contextZh" class="text-sm text-learning-accent-secondary italic">
                "{{ contextZh }}"
              </p>
            </div>

            <div v-if="examples && examples.length > 0">
              <p class="text-xs font-medium text-learning-text-secondary uppercase tracking-wide mb-2">
                {{ t('Examples', '例句') }}
              </p>
              <ul class="space-y-1">
                <li
                  v-for="(example, index) in examples"
                  :key="index"
                  class="text-sm text-learning-text-muted"
                >
                  • {{ example }}
                  <span v-if="showZh && examplesZh && examplesZh[index]" class="text-learning-accent-secondary text-xs ml-1">
                    {{ examplesZh[index] }}
                  </span>
                </li>
              </ul>
            </div>
          </div>

          <div class="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
            <button
              @click.stop="emit('markReviewed', word)"
              class="text-xs text-learning-accent-tertiary hover:text-learning-accent-tertiary/80 transition-colors"
            >
              {{ t('Mark as reviewed', '標記為已複習') }}
            </button>
            <p class="text-xs text-learning-text-muted">
              {{ t('Click to flip back', '點擊翻轉回來') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.perspective-1000 {
  perspective: 1000px;
}

.backface-hidden {
  backface-visibility: hidden;
}

.rotate-y-180 {
  transform: rotateY(180deg);
}

.transform-style-preserve-3d {
  transform-style: preserve-3d;
}
</style>