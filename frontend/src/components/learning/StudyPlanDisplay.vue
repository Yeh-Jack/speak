<script setup lang="ts">
import { ref, computed } from 'vue';
import BaseButton from '@/components/common/BaseButton.vue';

interface VocabularyItem {
  word: string;
  word_zh?: string;
  definition: string;
  definition_zh?: string;
  context?: string;
  context_zh?: string;
  cefr_level?: string;
  cefr_level_zh?: string;
  pronunciation?: string;
  examples?: string[];
  examples_zh?: string[];
}

interface GrammarItem {
  pattern: string;
  pattern_zh?: string;
  explanation: string;
  explanation_zh?: string;
  examples: string[];
  examples_zh?: string[];
}

interface StudyObjective {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  type: 'vocabulary' | 'grammar' | 'pronunciation' | 'listening' | 'speaking';
}

interface StudyPlan {
  objectives: StudyObjective[];
  vocabulary: VocabularyItem[];
  grammar: GrammarItem[];
  totalChunks: number;
  completedChunks: number;
  estimatedMinutes: number;
}

interface Props {
  plan: StudyPlan;
  currentChunkIndex: number;
  isLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
});

const emit = defineEmits<{
  startLearning: [];
  selectObjective: [objectiveId: string];
  toggleObjective: [objectiveId: string];
}>();

const activeTab = ref<'overview' | 'vocabulary' | 'grammar' | 'pronunciation'>('vocabulary');
const showZh = ref(true);

const progress = computed(() => {
  if (props.plan.totalChunks === 0) return 0;
  return Math.round((props.plan.completedChunks / props.plan.totalChunks) * 100);
});

const vocabularyItems = computed(() => props.plan.vocabulary || []);

const grammarItems = computed(() => props.plan.grammar || []);

const completedVocabulary = computed(() =>
  vocabularyItems.value.length
);

const objectiveIcon = (type: StudyObjective['type']) => {
  const icons: Record<string, string> = {
    vocabulary: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
    grammar: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    pronunciation: 'M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z',
    listening: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z',
    speaking: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z',
  };
  return icons[type] || icons.vocabulary;
};

const objectiveColor = (type: StudyObjective['type']) => {
  const colors: Record<string, string> = {
    vocabulary: 'text-learning-accent-secondary',
    grammar: 'text-purple-400',
    pronunciation: 'text-learning-accent-primary',
    listening: 'text-learning-accent-tertiary',
    speaking: 'text-green-400',
  };
  return colors[type] || 'text-gray-400';
};

const cefrLevelColor = (level: string | undefined) => {
  if (!level) return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  const upperLevel = level.toUpperCase();
  if (upperLevel === 'A1' || upperLevel === 'A2') return 'bg-green-500/20 text-green-400 border-green-500/30';
  if (upperLevel === 'B1' || upperLevel === 'B2') return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
  if (upperLevel === 'C1' || upperLevel === 'C2') return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
  return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
};
</script>

<template>
  <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary overflow-hidden">
    <div class="p-5 border-b border-learning-bg-tertiary">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold font-display text-learning-text-primary">
          Study Plan / 學習計劃
        </h2>
        <div class="flex items-center gap-2">
          <button
            @click="showZh = !showZh"
            class="px-2 py-1 text-xs rounded border transition-colors"
            :class="showZh ? 'bg-learning-accent-primary text-white border-learning-accent-primary' : 'bg-learning-bg-primary text-learning-text-secondary border-learning-bg-tertiary hover:border-learning-accent-primary'"
          >
            中文
          </button>
          <span class="text-sm text-learning-text-secondary">
            Chunk {{ currentChunkIndex + 1 }} / {{ plan.totalChunks }}
          </span>
        </div>
      </div>

      <div class="mb-4">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-learning-text-secondary">Progress / 進度</span>
          <span class="text-learning-text-primary font-medium">{{ progress }}%</span>
        </div>
        <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-learning-accent-primary to-learning-accent-secondary rounded-full transition-all duration-500"
            :style="{ width: `${progress}%` }"
          />
        </div>
      </div>

      <div class="flex items-center gap-4 text-sm">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-learning-accent-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-learning-text-secondary">
            ~{{ plan.estimatedMinutes }} min / 分鐘
          </span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span class="text-learning-text-secondary">
            {{ completedVocabulary }} words / 單詞
          </span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span class="text-learning-text-secondary">
            {{ grammarItems.length }} patterns / 句型
          </span>
        </div>
      </div>
    </div>

    <div class="flex border-b border-learning-bg-tertiary">
      <button
        v-for="tab in ['vocabulary', 'grammar'] as const"
        :key="tab"
        @click="activeTab = tab"
        class="flex-1 px-4 py-3 text-sm font-medium transition-colors relative"
        :class="activeTab === tab ? 'text-learning-accent-primary' : 'text-learning-text-secondary hover:text-learning-text-primary'"
      >
        {{ tab === 'vocabulary' ? 'Vocabulary / 詞匯' : 'Grammar / 文法' }}
        <div
          v-if="activeTab === tab"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-learning-accent-primary"
        />
      </button>
    </div>

    <div class="p-5 max-h-96 overflow-y-auto">
      <div v-if="isLoading" class="flex items-center justify-center py-8">
        <div class="animate-spin w-8 h-8 border-2 border-learning-accent-primary border-t-transparent rounded-full" />
      </div>

      <div v-else-if="activeTab === 'vocabulary'" class="space-y-3">
        <div
          v-for="(vocab, index) in vocabularyItems"
          :key="index"
          class="p-3 bg-learning-bg-primary rounded-lg hover:bg-learning-bg-secondary transition-colors"
        >
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span
              v-if="vocab.cefr_level"
              class="px-2 py-0.5 text-xs font-medium rounded border"
              :class="cefrLevelColor(vocab.cefr_level)"
            >
              {{ vocab.cefr_level }}
            </span>
            <span class="font-medium text-learning-text-primary">{{ vocab.word }}</span>
            <span v-if="showZh && vocab.word_zh" class="text-sm text-learning-accent-secondary">{{ vocab.word_zh }}</span>
            <span v-if="vocab.pronunciation" class="text-sm text-learning-text-muted">{{ vocab.pronunciation }}</span>
          </div>
          <p class="text-sm text-learning-text-secondary mb-1">{{ vocab.definition }}</p>
          <p v-if="showZh && vocab.definition_zh" class="text-sm text-learning-text-muted mb-2">{{ vocab.definition_zh }}</p>
          <p v-if="vocab.context" class="text-sm text-learning-text-muted italic mb-2">"{{ vocab.context }}"</p>
          <p v-if="showZh && vocab.context_zh" class="text-sm text-learning-accent-secondary/70 italic mb-2">"{{ vocab.context_zh }}"</p>
          <div v-if="vocab.examples && vocab.examples.length > 0">
            <p class="text-xs font-medium text-learning-text-muted uppercase tracking-wide mb-1">Examples / 例句:</p>
            <ul class="space-y-1">
              <li
                v-for="(example, exIndex) in vocab.examples"
                :key="exIndex"
                class="text-sm text-learning-text-secondary pl-2 border-l-2 border-learning-accent-secondary/30"
              >
                {{ example }}
                <span v-if="showZh && vocab.examples_zh && vocab.examples_zh[exIndex]" class="text-learning-accent-secondary/70 text-xs ml-1">
                  {{ vocab.examples_zh[exIndex] }}
                </span>
              </li>
            </ul>
          </div>
        </div>
        <p v-if="vocabularyItems.length === 0" class="text-center text-learning-text-muted py-4">
          No vocabulary items / 暫無詞匯
        </p>
      </div>

      <div v-else-if="activeTab === 'grammar'" class="space-y-3">
        <div
          v-for="(grammar, index) in grammarItems"
          :key="index"
          class="p-3 bg-learning-bg-primary rounded-lg"
        >
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span class="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded border border-purple-500/30">
              Pattern {{ index + 1 }}
            </span>
            <code class="text-sm bg-learning-bg-secondary px-2 py-0.5 rounded text-learning-text-primary">{{ grammar.pattern }}</code>
            <span v-if="showZh && grammar.pattern_zh" class="text-sm text-purple-400">{{ grammar.pattern_zh }}</span>
          </div>
          <p class="text-sm text-learning-text-secondary mb-1">{{ grammar.explanation }}</p>
          <p v-if="showZh && grammar.explanation_zh" class="text-sm text-learning-accent-secondary mb-3">{{ grammar.explanation_zh }}</p>
          <div v-if="grammar.examples && grammar.examples.length > 0">
            <p class="text-xs font-medium text-learning-text-muted uppercase tracking-wide mb-1">Examples / 例句:</p>
            <ul class="space-y-1">
              <li
                v-for="(example, exIndex) in grammar.examples"
                :key="exIndex"
                class="text-sm text-learning-text-secondary pl-2 border-l-2 border-purple-500/30"
              >
                {{ example }}
                <span v-if="showZh && grammar.examples_zh && grammar.examples_zh[exIndex]" class="text-purple-400 text-xs ml-1">
                  {{ grammar.examples_zh[exIndex] }}
                </span>
              </li>
            </ul>
          </div>
        </div>
        <p v-if="grammarItems.length === 0" class="text-center text-learning-text-muted py-4">
          No grammar patterns / 暫無句型
        </p>
      </div>
    </div>
  </div>
</template>