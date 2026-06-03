<script setup lang="ts">
import { ref, computed } from 'vue';
import BaseButton from '@/components/common/BaseButton.vue';

export interface StudyObjective {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  type: 'vocabulary' | 'grammar' | 'pronunciation' | 'listening' | 'speaking';
}

export interface StudyPlan {
  objectives: StudyObjective[];
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

const activeTab = ref<'overview' | 'vocabulary' | 'grammar' | 'pronunciation'>('overview');

const progress = computed(() => {
  if (props.plan.totalChunks === 0) return 0;
  return Math.round((props.plan.completedChunks / props.plan.totalChunks) * 100);
});

const vocabularyObjectives = computed(() =>
  props.plan.objectives.filter((obj) => obj.type === 'vocabulary')
);

const grammarObjectives = computed(() =>
  props.plan.objectives.filter((obj) => obj.type === 'grammar')
);

const pronunciationObjectives = computed(() =>
  props.plan.objectives.filter((obj) => obj.type === 'pronunciation')
);

const completedCount = computed(() =>
  props.plan.objectives.filter((obj) => obj.completed).length
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
</script>

<template>
  <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary overflow-hidden">
    <div class="p-5 border-b border-learning-bg-tertiary">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold font-display text-learning-text-primary">
          Study Plan
        </h2>
        <span class="text-sm text-learning-text-secondary">
          Chunk {{ currentChunkIndex + 1 }} of {{ plan.totalChunks }}
        </span>
      </div>

      <div class="mb-4">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-learning-text-secondary">Progress</span>
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
            ~{{ plan.estimatedMinutes }} min
          </span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-learning-text-secondary">
            {{ completedCount }}/{{ plan.objectives.length }} completed
          </span>
        </div>
      </div>
    </div>

    <div class="flex border-b border-learning-bg-tertiary">
      <button
        v-for="tab in ['overview', 'vocabulary', 'grammar', 'pronunciation'] as const"
        :key="tab"
        @click="activeTab = tab"
        class="flex-1 px-4 py-3 text-sm font-medium transition-colors relative"
        :class="activeTab === tab ? 'text-learning-accent-primary' : 'text-learning-text-secondary hover:text-learning-text-primary'"
      >
        {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
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

      <div v-else-if="activeTab === 'overview'" class="space-y-3">
        <div
          v-for="objective in plan.objectives"
          :key="objective.id"
          @click="emit('selectObjective', objective.id)"
          class="flex items-start gap-3 p-3 bg-learning-bg-primary rounded-lg hover:bg-learning-bg-secondary cursor-pointer transition-colors"
        >
          <button
            @click.stop="emit('toggleObjective', objective.id)"
            class="mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors"
            :class="objective.completed
              ? 'bg-learning-accent-primary border-learning-accent-primary'
              : 'border-learning-text-muted hover:border-learning-text-secondary'"
          >
            <svg v-if="objective.completed" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </button>

          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <svg
                class="w-4 h-4"
                :class="objectiveColor(objective.type)"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="objectiveIcon(objective.type)" />
              </svg>
              <span class="font-medium text-learning-text-primary">{{ objective.title }}</span>
            </div>
            <p class="text-sm text-learning-text-secondary">{{ objective.description }}</p>
          </div>
        </div>

        <BaseButton
          v-if="!plan.completedChunks"
          class="w-full mt-4"
          @click="emit('startLearning')"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Start Learning
        </BaseButton>
      </div>

      <div v-else-if="activeTab === 'vocabulary'" class="space-y-3">
        <div
          v-for="objective in vocabularyObjectives"
          :key="objective.id"
          class="p-3 bg-learning-bg-primary rounded-lg"
        >
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span class="font-medium text-learning-text-primary">{{ objective.title }}</span>
          </div>
          <p class="text-sm text-learning-text-secondary">{{ objective.description }}</p>
        </div>
        <p v-if="vocabularyObjectives.length === 0" class="text-center text-learning-text-muted py-4">
          No vocabulary objectives
        </p>
      </div>

      <div v-else-if="activeTab === 'grammar'" class="space-y-3">
        <div
          v-for="objective in grammarObjectives"
          :key="objective.id"
          class="p-3 bg-learning-bg-primary rounded-lg"
        >
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="font-medium text-learning-text-primary">{{ objective.title }}</span>
          </div>
          <p class="text-sm text-learning-text-secondary">{{ objective.description }}</p>
        </div>
        <p v-if="grammarObjectives.length === 0" class="text-center text-learning-text-muted py-4">
          No grammar objectives
        </p>
      </div>

      <div v-else-if="activeTab === 'pronunciation'" class="space-y-3">
        <div
          v-for="objective in pronunciationObjectives"
          :key="objective.id"
          class="p-3 bg-learning-bg-primary rounded-lg"
        >
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
            <span class="font-medium text-learning-text-primary">{{ objective.title }}</span>
          </div>
          <p class="text-sm text-learning-text-secondary">{{ objective.description }}</p>
        </div>
        <p v-if="pronunciationObjectives.length === 0" class="text-center text-learning-text-muted py-4">
          No pronunciation objectives
        </p>
      </div>
    </div>
  </div>
</template>