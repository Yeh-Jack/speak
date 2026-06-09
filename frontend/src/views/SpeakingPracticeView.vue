<script setup lang="ts">
import { ref } from 'vue';

const isRecording = ref(false);
const audioLevel = ref(0);
const selectedTopic = ref('daily');
const practiceHistory = ref([
  { id: '1', title: 'Ordering Coffee / 點咖啡', date: '2026-06-02', score: 85, duration: '3:45' },
  { id: '2', title: 'Job Interview / 工作面試', date: '2026-06-01', score: 78, duration: '5:20' },
]);

const topics = [
  { id: 'daily', label: 'Daily Conversation / 日常對話', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
  { id: 'business', label: 'Business English / 商務英語', icon: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  { id: 'travel', label: 'Travel & Tourism / 旅遊', icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z' },
  { id: 'academic', label: 'Academic Discussion / 學術討論', icon: 'M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z' },
];

function startRecording() {
  isRecording.value = true;
  const interval = setInterval(() => {
    audioLevel.value = Math.random() * 100;
  }, 100);
  setTimeout(() => {
    clearInterval(interval);
    isRecording.value = false;
    audioLevel.value = 0;
  }, 5000);
}
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <header class="sticky top-0 z-40 bg-learning-bg-secondary border-b border-learning-bg-tertiary">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <router-link to="/" class="text-2xl font-bold font-display text-learning-text-primary">
          Speak
        </router-link>
        <nav class="flex items-center gap-6">
          <router-link to="/" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
            Dashboard / 首頁
          </router-link>
          <router-link to="/speaking" class="text-learning-accent-primary">
            Speaking / 口說
          </router-link>
        </nav>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-learning-accent-primary flex items-center justify-center text-white font-medium">
            U
          </div>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold font-display text-learning-text-primary mb-2">
          Speaking Practice / 口說練習
        </h1>
        <p class="text-learning-text-secondary">
          Improve your pronunciation with AI-powered shadowing and speech recognition / 使用 AI 驅動的跟讀和語音辨識提升發音
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6 mb-6">
            <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Select a Topic / 選擇主題
            </h2>
            <div class="grid grid-cols-2 gap-4 mb-6">
              <button
                v-for="topic in topics"
                :key="topic.id"
                @click="selectedTopic = topic.id"
                class="p-4 rounded-xl border transition-all text-left"
                :class="selectedTopic === topic.id
                  ? 'border-learning-accent-primary bg-learning-accent-primary/10'
                  : 'border-learning-bg-tertiary hover:border-learning-accent-primary/50'"
              >
                <svg class="w-6 h-6 mb-2" :class="selectedTopic === topic.id ? 'text-learning-accent-primary' : 'text-learning-text-secondary'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="topic.icon" />
                </svg>
                <p class="font-medium text-learning-text-primary">{{ topic.label }}</p>
              </button>
            </div>

            <div class="flex flex-col items-center justify-center py-12 bg-learning-bg-primary rounded-xl">
              <div class="relative mb-6">
                <div
                  v-if="isRecording"
                  class="absolute inset-0 flex items-center justify-center"
                >
                  <div class="flex gap-1">
                    <div
                      v-for="i in 8"
                      :key="i"
                      class="w-1 bg-learning-accent-primary rounded-full animate-pulse"
                      :style="{
                        height: `${20 + Math.random() * 40}px`,
                        animationDelay: `${i * 0.1}s`
                      }"
                    />
                  </div>
                </div>
                <button
                  @click="startRecording"
                  class="relative w-24 h-24 rounded-full transition-all flex items-center justify-center"
                  :class="isRecording
                    ? 'bg-red-500 animate-pulse'
                    : 'bg-learning-accent-primary hover:bg-learning-accent-primary/90'"
                >
                  <svg v-if="!isRecording" class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                  </svg>
                  <div v-else class="w-8 h-8 bg-white rounded-full" />
                </button>
              </div>
              <p class="text-learning-text-secondary text-center">
                {{ isRecording ? 'Recording... Speak now! / 錄音中... 請說話！' : 'Click to start recording / 點擊開始錄音' }}
              </p>
              <p class="text-learning-text-muted text-sm mt-2">
                Practice speaking for at least 30 seconds / 練習說話至少 30 秒
              </p>
            </div>
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-6">
            <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Practice Tips / 練習技巧
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="p-4 bg-learning-bg-primary rounded-lg">
                <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center mb-3">
                  <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 class="font-medium text-learning-text-primary mb-1">Shadowing / 跟讀</h3>
                <p class="text-sm text-learning-text-muted">Listen and repeat immediately after hearing / 聽完立即重複</p>
              </div>
              <div class="p-4 bg-learning-bg-primary rounded-lg">
                <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center mb-3">
                  <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 class="font-medium text-learning-text-primary mb-1">Focus on Fluency / 專注流利度</h3>
                <p class="text-sm text-learning-text-muted">Don't worry about mistakes, keep talking / 不要擔心錯誤，繼續說</p>
              </div>
              <div class="p-4 bg-learning-bg-primary rounded-lg">
                <div class="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-3">
                  <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </div>
                <h3 class="font-medium text-learning-text-primary mb-1">Record Yourself / 錄下自己的聲音</h3>
                <p class="text-sm text-learning-text-muted">Listen back to identify areas to improve / 回聽以找出需改進之處</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5 mb-6">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Today's Practice / 今日練習
            </h3>
            <div class="text-center py-6">
              <div class="relative w-32 h-32 mx-auto mb-4">
                <svg class="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="8"
                    class="text-learning-bg-primary"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="8"
                    stroke-dasharray="352"
                    stroke-dashoffset="176"
                    class="text-learning-accent-primary"
                    stroke-linecap="round"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-3xl font-bold text-learning-text-primary">5</span>
                  <span class="text-xs text-learning-text-muted">of 15 min / 15分鐘中</span>
                </div>
              </div>
              <p class="text-sm text-learning-text-secondary mb-4">
                Keep going! Practice makes perfect. / 繼續加油！練習造就完美。
              </p>
              <div class="flex items-center justify-center gap-2 text-sm text-learning-text-muted">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                10 min remaining / 剩餘10分鐘
              </div>
            </div>
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Recent Practice / 最近練習
            </h3>
            <div class="space-y-3">
              <div
                v-for="session in practiceHistory"
                :key="session.id"
                class="p-3 bg-learning-bg-primary rounded-lg"
              >
                <div class="flex items-start justify-between mb-2">
                  <h4 class="font-medium text-learning-text-primary">{{ session.title }}</h4>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :class="session.score >= 80 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'"
                  >
                    {{ session.score }}%
                  </span>
                </div>
                <div class="flex items-center gap-3 text-xs text-learning-text-muted">
                  <span>{{ session.date }}</span>
                  <span>Duration: {{ session.duration }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>