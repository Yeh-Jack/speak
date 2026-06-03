<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useVideoStore } from '@/stores';
import VideoPlayer from '@/components/video/VideoPlayer.vue';
import StudyPlanDisplay from '@/components/learning/StudyPlanDisplay.vue';
import VocabularyCard from '@/components/learning/VocabularyCard.vue';
import ShadowingMode from '@/components/learning/ShadowingMode.vue';
import type { StudyPlan, TranscriptSegment } from '@/types';

const route = useRoute();
const videoStore = useVideoStore();

const videoId = computed(() => route.params.id as string);

const showShadowingMode = ref(false);
const videoRef = ref<InstanceType<typeof VideoPlayer> | null>(null);
const currentTime = ref(0);

const mockVideoUrl = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4';

const mockTranscript: TranscriptSegment[] = [
  { start: 0, end: 5, text: 'Welcome to this English learning video.' },
  { start: 5, end: 10, text: 'Today we are going to learn some new vocabulary.' },
  { start: 10, end: 15, text: 'Pay attention to the pronunciation of each word.' },
  { start: 15, end: 20, text: 'Repeat after me to practice your speaking skills.' },
  { start: 20, end: 25, text: 'This is an excellent opportunity to improve your English.' },
  { start: 25, end: 30, text: 'Let us start with the first vocabulary word.' },
  { start: 30, end: 35, text: 'Ephemeral - lasting for a very short time.' },
  { start: 35, end: 40, text: 'The ephemeral nature of cherry blossoms makes them even more beautiful.' },
  { start: 40, end: 45, text: 'Mundane - lacking interest or excitement.' },
  { start: 45, end: 50, text: 'She wanted to escape her mundane daily routine.' },
];

const mockStudyPlan: StudyPlan = {
  id: '1',
  video_id: '1',
  chunk_index: 0,
  objectives: [
    { id: '1', title: 'Learn 10 new vocabulary words', description: 'Focus on common English words used in daily conversation', completed: false, type: 'vocabulary' },
    { id: '2', title: 'Practice pronunciation', description: 'Listen and repeat each word to improve accent', completed: false, type: 'pronunciation' },
    { id: '3', title: 'Shadowing practice', description: 'Repeat sentences immediately after hearing them', completed: false, type: 'speaking' },
    { id: '4', title: 'Understand grammar patterns', description: 'Learn how words combine to form sentences', completed: false, type: 'grammar' },
  ],
  vocabulary: [
    { word: 'ephemeral', definition: 'lasting for a very short time', context: 'The ephemeral beauty of the sunset', cefr_level: 'B2', pronunciation: '/ɪˈfem.ər.əl/', examples: ['Fame can be ephemeral.', 'The ephemeral nature of fashion trends.'] },
    { word: 'mundane', definition: 'lacking interest or excitement; dull', context: 'Everyday mundane tasks', cefr_level: 'B1', pronunciation: '/mʌnˈdeɪn/', examples: ['Mundane office work.', 'She found cooking mundane.', 'He escaped his mundane life.'] },
    { word: 'profound', definition: 'very great or intense; having deep insight', context: 'A profound impact on society', cefr_level: 'B2', pronunciation: '/prəˈfaʊnd/', examples: ['The book had a profound effect on me.', 'He made a profound observation.'] },
    { word: 'eloquent', definition: 'fluent or persuasive in speaking or writing', context: 'An eloquent speaker', cefr_level: 'C1', pronunciation: '/ˈel.ə.kwənt/', examples: ['She gave an eloquent speech.', 'His eloquent writing moved the audience.'] },
    { word: 'resilient', definition: 'able to recover quickly from difficulties', context: 'A resilient economy', cefr_level: 'B2', pronunciation: '/rɪˈzɪl.i.ənt/', examples: ['Children are often very resilient.', 'The resilient spirit of the team.'] },
  ],
  grammar: [
    { pattern: 'The more... the more', explanation: 'Used to express that two things change together', examples: ['The more you practice, the better you get.', 'The more she studied, the more she understood.'] },
    { pattern: 'Passive voice', explanation: 'Subject receives the action', examples: ['The lesson was taught by the teacher.', 'English is spoken worldwide.'] },
  ],
  totalChunks: 1,
  completedChunks: 0,
  estimatedMinutes: 30,
  created_at: new Date().toISOString(),
};

const shadowingSentences = computed(() =>
  mockTranscript.map((seg, index) => ({
    id: `sentence-${index}`,
    text: seg.text,
    startTime: seg.start,
    endTime: seg.end,
    translation: seg.text,
  }))
);

function handleTimeUpdate(time: number) {
  currentTime.value = time;
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

onMounted(() => {
  videoStore.setVideo({
    id: videoId.value,
    title: 'Sample English Learning Video',
    description: 'Learn English with this engaging video',
    source_type: 'youtube',
    youtube_url: 'https://youtube.com/watch?v=example',
    file_path: mockVideoUrl,
    duration: 60,
    chunk_duration: 30,
    status: 'ready',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  });
  videoStore.setChunks([
    {
      id: 'chunk-0',
      video_id: videoId.value,
      chunk_index: 0,
      start_time: 0,
      end_time: 30,
      duration: 30,
      transcript: mockTranscript,
      status: 'ready',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ]);
  videoStore.setStudyPlan(0, mockStudyPlan);
});
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <header class="bg-learning-bg-secondary border-b border-learning-bg-tertiary">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link to="/" class="text-xl font-bold font-display text-learning-text-primary">
            Speak
          </router-link>
          <span class="text-learning-text-muted">/</span>
          <span class="text-learning-text-secondary">Learning</span>
        </div>
        <router-link
          to="/courses"
          class="text-sm text-learning-text-secondary hover:text-learning-text-primary transition-colors"
        >
          Back to Courses
        </router-link>
      </div>
    </header>

    <main class="container mx-auto px-4 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary overflow-hidden">
            <VideoPlayer
              ref="videoRef"
              :src="mockVideoUrl"
              :transcript="mockTranscript"
              @time-update="handleTimeUpdate"
            />
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary flex items-center gap-2">
                <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                Chunks
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
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="videoStore.currentChunkIndex === index
                  ? 'bg-learning-accent-primary text-white'
                  : 'bg-learning-bg-primary text-learning-text-secondary hover:bg-learning-bg-secondary'"
              >
                Chunk {{ index + 1 }}
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
                :definition="vocab.definition"
                :context="vocab.context"
                :cefr-level="vocab.cefr_level"
                :pronunciation="vocab.pronunciation"
                :examples="vocab.examples"
                :is-saved="videoStore.isVocabularySaved(vocab.word)"
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
            v-if="videoStore.currentStudyPlan"
            :plan="videoStore.currentStudyPlan"
            :current-chunk-index="videoStore.currentChunkIndex"
            @start-learning="handleStartLearning"
          />

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Quick Actions
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
                  <p class="font-medium text-learning-text-primary">Shadowing Mode</p>
                  <p class="text-sm text-learning-text-secondary">Practice speaking</p>
                </div>
              </button>

              <button class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary hover:bg-learning-bg-secondary rounded-lg transition-colors text-left">
                <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center">
                  <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-learning-text-primary">Review Vocabulary</p>
                  <p class="text-sm text-learning-text-secondary">{{ videoStore.savedVocabulary.size }} saved</p>
                </div>
              </button>

              <button class="w-full flex items-center gap-3 px-4 py-3 bg-learning-bg-primary hover:bg-learning-bg-secondary rounded-lg transition-colors text-left">
                <div class="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-learning-text-primary">Grammar Notes</p>
                  <p class="text-sm text-learning-text-secondary">{{ videoStore.currentStudyPlan?.grammar.length || 0 }} patterns</p>
                </div>
              </button>
            </div>
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Progress
            </h3>
            <div class="space-y-4">
              <div>
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-learning-text-secondary">Vocabulary learned</span>
                  <span class="text-learning-text-primary">4 / 10</span>
                </div>
                <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                  <div class="h-full bg-learning-accent-secondary rounded-full" style="width: 40%" />
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-learning-text-secondary">Shadowing practice</span>
                  <span class="text-learning-text-primary">0 / 5</span>
                </div>
                <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                  <div class="h-full bg-learning-accent-primary rounded-full" style="width: 0%" />
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm mb-2">
                  <span class="text-learning-text-secondary">Grammar patterns</span>
                  <span class="text-learning-text-primary">0 / 2</span>
                </div>
                <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                  <div class="h-full bg-purple-400 rounded-full" style="width: 0%" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>