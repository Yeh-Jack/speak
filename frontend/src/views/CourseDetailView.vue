<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const courseId = computed(() => route.params.id as string);

const course = ref({
  id: '1',
  title: 'English for Beginners',
  description: 'Start your English learning journey with essential vocabulary and grammar. This course covers basic greetings, numbers, and everyday phrases.',
  thumbnail: 'https://picsum.photos/seed/course1/640/360',
  videoCount: 12,
  duration: '2h 30m',
  progress: 35,
  videos: [
    { id: '1', title: 'Basic Greetings', duration: '8:30', completed: true, thumbnail: 'https://picsum.photos/seed/v1/320/180' },
    { id: '2', title: 'Numbers and Counting', duration: '10:15', completed: true, thumbnail: 'https://picsum.photos/seed/v2/320/180' },
    { id: '3', title: 'Days of the Week', duration: '7:45', completed: false, thumbnail: 'https://picsum.photos/seed/v3/320/180' },
    { id: '4', title: 'Months and Seasons', duration: '9:20', completed: false, thumbnail: 'https://picsum.photos/seed/v4/320/180' },
    { id: '5', title: 'Family Members', duration: '11:00', completed: false, thumbnail: 'https://picsum.photos/seed/v5/320/180' },
    { id: '6', title: 'Colors and Shapes', duration: '8:15', completed: false, thumbnail: 'https://picsum.photos/seed/v6/320/180' },
  ],
});

const completedCount = computed(() => course.value.videos.filter(v => v.completed).length);

function goToVideo(videoId: string) {
  router.push(`/videos/${videoId}`);
}

function goBack() {
  router.push('/courses');
}
</script>

<template>
  <div class="min-h-screen bg-learning-bg-primary">
    <header class="bg-learning-bg-secondary border-b border-learning-bg-tertiary">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <router-link to="/" class="text-2xl font-bold font-display text-learning-text-primary">
            Speak
          </router-link>
          <span class="text-learning-text-muted">/</span>
          <router-link to="/courses" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
            Courses
          </router-link>
          <span class="text-learning-text-muted">/</span>
          <span class="text-learning-text-primary">{{ course.title }}</span>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="goBack"
            class="flex items-center gap-2 px-3 py-1.5 text-sm text-learning-text-secondary hover:text-learning-text-primary transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
          <div class="relative aspect-video bg-learning-bg-secondary rounded-xl overflow-hidden mb-6">
            <img :src="course.thumbnail" :alt="course.title" class="w-full h-full object-cover opacity-60" />
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-16 h-16 rounded-full bg-learning-accent-primary/90 flex items-center justify-center cursor-pointer hover:scale-110 transition-transform" @click="goToVideo('3')">
                <svg class="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </div>
            </div>
          </div>

          <h1 class="text-2xl font-bold font-display text-learning-text-primary mb-2">
            {{ course.title }}
          </h1>
          <p class="text-learning-text-secondary mb-6">
            {{ course.description }}
          </p>

          <div class="flex items-center gap-6 mb-8">
            <span class="flex items-center gap-2 text-sm text-learning-text-secondary">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              {{ course.videoCount }} videos
            </span>
            <span class="flex items-center gap-2 text-sm text-learning-text-secondary">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ course.duration }}
            </span>
            <span class="flex items-center gap-2 text-sm text-learning-text-secondary">
              <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ completedCount }}/{{ course.videoCount }} completed
            </span>
          </div>

          <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
            Course Content
          </h2>

          <div class="space-y-3">
            <div
              v-for="(video, index) in course.videos"
              :key="video.id"
              @click="goToVideo(video.id)"
              class="flex items-center gap-4 p-4 bg-learning-surface rounded-xl border border-learning-bg-tertiary cursor-pointer hover:border-learning-accent-primary/50 transition-colors group"
              :class="{ 'opacity-60': video.completed }"
            >
              <div class="relative w-24 h-14 rounded-lg overflow-hidden bg-learning-bg-primary flex-shrink-0">
                <img :src="video.thumbnail" :alt="video.title" class="w-full h-full object-cover" />
                <div v-if="video.completed" class="absolute inset-0 bg-green-500/20 flex items-center justify-center">
                  <svg class="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                  </svg>
                </div>
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-sm text-learning-text-muted font-mono">{{ index + 1 }}.</span>
                  <h3 class="font-medium text-learning-text-primary truncate group-hover:text-learning-accent-secondary transition-colors">
                    {{ video.title }}
                  </h3>
                </div>
                <p class="text-sm text-learning-text-muted">{{ video.duration }}</p>
              </div>

              <svg class="w-5 h-5 text-learning-text-muted group-hover:text-learning-accent-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>

        <div>
          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5 mb-6">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Your Progress
            </h3>
            <div class="mb-4">
              <div class="flex justify-between text-sm mb-2">
                <span class="text-learning-text-secondary">Overall Progress</span>
                <span class="text-learning-text-primary font-medium">{{ course.progress }}%</span>
              </div>
              <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-learning-accent-primary to-learning-accent-secondary rounded-full transition-all"
                  :style="{ width: `${course.progress}%` }"
                />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4 text-center">
              <div class="p-3 bg-learning-bg-primary rounded-lg">
                <p class="text-2xl font-bold text-learning-accent-primary">{{ completedCount }}</p>
                <p class="text-xs text-learning-text-muted">Completed</p>
              </div>
              <div class="p-3 bg-learning-bg-primary rounded-lg">
                <p class="text-2xl font-bold text-learning-text-primary">{{ course.videoCount - completedCount }}</p>
                <p class="text-xs text-learning-text-muted">Remaining</p>
              </div>
            </div>
          </div>

          <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Continue Learning
            </h3>
            <button
              v-if="course.videos.find(v => !v.completed)"
              @click="goToVideo(course.videos.find(v => !v.completed)?.id || '1')"
              class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
              Resume Learning
            </button>
            <p v-else class="text-center text-learning-text-secondary text-sm py-4">
              Course completed! Great job!
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>