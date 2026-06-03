<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';

const router = useRouter();
const { user } = useAuth();

const recentVideos = ref([
  { id: '1', title: 'English Grammar Basics', duration: '12:30', progress: 65, thumbnail: 'https://picsum.photos/seed/video1/320/180' },
  { id: '2', title: 'Business English Vocabulary', duration: '18:45', progress: 30, thumbnail: 'https://picsum.photos/seed/video2/320/180' },
]);

const stats = ref({
  wordsLearned: 47,
  hoursLearned: 2.5,
  streakDays: 7,
  sentencesPracticed: 23,
});

function goToVideo(videoId: string) {
  router.push(`/videos/${videoId}`);
}

function goToCourses() {
  router.push('/courses');
}

function goToSpeaking() {
  router.push('/speaking');
}
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <header class="bg-learning-bg-secondary border-b border-learning-bg-tertiary">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <router-link to="/" class="text-2xl font-bold font-display text-learning-text-primary">
          Speak
        </router-link>
        <nav class="flex items-center gap-6">
          <router-link to="/" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
            Dashboard
          </router-link>
          <router-link to="/courses" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
            Courses
          </router-link>
          <router-link to="/speaking" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
            Speaking
          </router-link>
        </nav>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-learning-accent-primary flex items-center justify-center text-white font-medium">
            {{ user?.email?.[0]?.toUpperCase() || 'U' }}
          </div>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold font-display text-learning-text-primary mb-2">
          Welcome back, {{ user?.email?.split('@')[0] }}!
        </h1>
        <p class="text-learning-text-secondary">Continue your English learning journey</p>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-secondary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">Words Learned</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.wordsLearned }}</p>
        </div>

        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-primary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">Hours Learned</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.hoursLearned }}</p>
        </div>

        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-learning-accent-tertiary/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-learning-accent-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">Day Streak</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.streakDays }}</p>
        </div>

        <div class="bg-learning-surface rounded-xl p-5 border border-learning-bg-tertiary">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <span class="text-learning-text-secondary text-sm">Sentences</span>
          </div>
          <p class="text-3xl font-bold text-learning-text-primary">{{ stats.sentencesPracticed }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div class="lg:col-span-2">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold font-display text-learning-text-primary">Continue Learning</h2>
            <button class="text-sm text-learning-accent-secondary hover:text-learning-accent-secondary/80 transition-colors" @click="goToCourses">
              View All
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="video in recentVideos"
              :key="video.id"
              @click="goToVideo(video.id)"
              class="bg-learning-surface rounded-xl overflow-hidden border border-learning-bg-tertiary cursor-pointer card-interactive group"
            >
              <div class="relative aspect-video bg-learning-bg-primary">
                <img :src="video.thumbnail" :alt="video.title" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                <div class="absolute inset-0 flex items-center justify-center">
                  <div class="w-12 h-12 rounded-full bg-learning-accent-primary/90 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </div>
                <span class="absolute bottom-2 right-2 px-2 py-0.5 bg-black/70 rounded text-xs text-white font-mono">
                  {{ video.duration }}
                </span>
              </div>
              <div class="p-4">
                <h3 class="font-medium text-learning-text-primary mb-2">{{ video.title }}</h3>
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-1.5 bg-learning-bg-primary rounded-full overflow-hidden">
                    <div
                      class="h-full bg-learning-accent-primary rounded-full"
                      :style="{ width: `${video.progress}%` }"
                    />
                  </div>
                  <span class="text-xs text-learning-text-secondary">{{ video.progress }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 class="text-xl font-semibold font-display text-learning-text-primary mb-4">Quick Actions</h2>

          <div class="space-y-3">
            <button
              @click="goToVideo('1')"
              class="w-full flex items-center gap-4 p-4 bg-learning-surface rounded-xl border border-learning-bg-tertiary hover:border-learning-accent-primary/50 transition-colors text-left group"
            >
              <div class="w-12 h-12 rounded-xl bg-learning-accent-primary/10 flex items-center justify-center group-hover:bg-learning-accent-primary/20 transition-colors">
                <svg class="w-6 h-6 text-learning-accent-primary" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-learning-text-primary">Start Video Learning</p>
                <p class="text-sm text-learning-text-secondary">Watch & study with subtitles</p>
              </div>
            </button>

            <button
              @click="goToSpeaking"
              class="w-full flex items-center gap-4 p-4 bg-learning-surface rounded-xl border border-learning-bg-tertiary hover:border-learning-accent-secondary/50 transition-colors text-left group"
            >
              <div class="w-12 h-12 rounded-xl bg-learning-accent-secondary/10 flex items-center justify-center group-hover:bg-learning-accent-secondary/20 transition-colors">
                <svg class="w-6 h-6 text-learning-accent-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-learning-text-primary">Speaking Practice</p>
                <p class="text-sm text-learning-text-secondary">Shadowing & pronunciation</p>
              </div>
            </button>

            <button
              @click="goToCourses"
              class="w-full flex items-center gap-4 p-4 bg-learning-surface rounded-xl border border-learning-bg-tertiary hover:border-purple-500/50 transition-colors text-left group"
            >
              <div class="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
                <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-learning-text-primary">Browse Courses</p>
                <p class="text-sm text-learning-text-secondary">Structured learning paths</p>
              </div>
            </button>
          </div>

          <div class="mt-6 p-4 bg-gradient-to-br from-learning-accent-primary/10 to-learning-accent-secondary/10 rounded-xl border border-learning-accent-primary/20">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-5 h-5 text-learning-accent-tertiary" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <span class="font-medium text-learning-text-primary">Daily Goal</span>
            </div>
            <p class="text-sm text-learning-text-secondary mb-3">Practice English for at least 15 minutes today</p>
            <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-learning-accent-primary to-learning-accent-secondary rounded-full" style="width: 65%" />
            </div>
            <p class="text-xs text-learning-text-muted mt-1">10 min remaining</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>