<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const courses = ref([
  {
    id: '1',
    title: 'English for Beginners',
    description: 'Start your English learning journey with essential vocabulary and grammar',
    thumbnail: 'https://picsum.photos/seed/course1/640/360',
    videoCount: 12,
    duration: '2h 30m',
    progress: 35,
    videos: [
      { id: '1', title: 'Basic Greetings', duration: '8:30', thumbnail: 'https://picsum.photos/seed/v1/320/180' },
      { id: '2', title: 'Numbers and Counting', duration: '10:15', thumbnail: 'https://picsum.photos/seed/v2/320/180' },
      { id: '3', title: 'Days of the Week', duration: '7:45', thumbnail: 'https://picsum.photos/seed/v3/320/180' },
    ],
  },
  {
    id: '2',
    title: 'Business English',
    description: 'Professional vocabulary and communication skills for the workplace',
    thumbnail: 'https://picsum.photos/seed/course2/640/360',
    videoCount: 8,
    duration: '3h 15m',
    progress: 0,
    videos: [],
  },
  {
    id: '3',
    title: 'IELTS Preparation',
    description: 'Comprehensive preparation for the IELTS exam',
    thumbnail: 'https://picsum.photos/seed/course3/640/360',
    videoCount: 20,
    duration: '8h 00m',
    progress: 0,
    videos: [],
  },
  {
    id: '4',
    title: 'Daily Conversations',
    description: 'Natural English phrases for everyday situations',
    thumbnail: 'https://picsum.photos/seed/course4/640/360',
    videoCount: 15,
    duration: '4h 45m',
    progress: 0,
    videos: [],
  },
]);

function goToCourse(courseId: string) {
  router.push(`/courses/${courseId}`);
}

function goToVideo(videoId: string) {
  router.push(`/videos/${videoId}`);
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
          <router-link to="/courses" class="text-learning-accent-primary transition-colors">
            Courses
          </router-link>
          <router-link to="/speaking" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
            Speaking
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
          Courses
        </h1>
        <p class="text-learning-text-secondary">
          Structured learning paths to improve your English
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="course in courses"
          :key="course.id"
          @click="goToCourse(course.id)"
          class="bg-learning-surface rounded-xl overflow-hidden border border-learning-bg-tertiary cursor-pointer card-interactive group"
        >
          <div class="relative aspect-video bg-learning-bg-primary">
            <img :src="course.thumbnail" :alt="course.title" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
            <div v-if="course.progress > 0" class="absolute top-3 right-3 px-2 py-1 bg-black/70 rounded text-xs text-white font-medium">
              {{ course.progress }}% complete
            </div>
          </div>
          <div class="p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-2">
              {{ course.title }}
            </h3>
            <p class="text-learning-text-secondary text-sm mb-4">
              {{ course.description }}
            </p>
            <div class="flex items-center gap-4 text-sm text-learning-text-muted">
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {{ course.videoCount }} videos
              </span>
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ course.duration }}
              </span>
            </div>

            <div v-if="course.progress > 0" class="mt-4">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-learning-text-secondary">Progress</span>
                <span class="text-learning-text-primary">{{ course.progress }}%</span>
              </div>
              <div class="h-1.5 bg-learning-bg-primary rounded-full overflow-hidden">
                <div
                  class="h-full bg-learning-accent-primary rounded-full transition-all"
                  :style="{ width: `${course.progress}%` }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>