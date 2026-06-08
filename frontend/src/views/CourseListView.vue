<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { courseService } from '@/services/course.service';
import { videoService } from '@/services/video.service';
import type { Course, Video } from '@/types';

const router = useRouter();

const courses = ref<Course[]>([]);
const videos = ref<Video[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

function formatDuration(duration: number): string {
  const hours = Math.floor(duration / 3600);
  const mins = Math.floor((duration % 3600) / 60);
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

function getCourseProgress(course: Course): number {
  if (!course.course_videos || course.course_videos.length === 0) return 0;
  const completed = course.course_videos.filter((cv, idx) => idx < course.current_video_index).length;
  return Math.round((completed / course.course_videos.length) * 100);
}

function getVideoCount(course: Course): number {
  return course.course_videos?.length || 0;
}

function goToCourse(courseId: string) {
  router.push(`/courses/${courseId}`);
}

function goToVideo(videoId: string) {
  router.push(`/videos/${videoId}`);
}

async function fetchCourses() {
  isLoading.value = true;
  error.value = null;
  try {
    courses.value = await courseService.getCourses();
    if (courses.value.length === 0) {
      videos.value = await videoService.getAllVideos();
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load courses';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchCourses();
});
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
          <router-link to="/courses" class="text-learning-accent-primary transition-colors">
            Courses / 課程
          </router-link>
          <router-link to="/speaking" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
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
          Courses / 課程
        </h1>
        <p class="text-learning-text-secondary">
          Structured learning paths to improve your English / 結構化學習路徑提升您的英語
        </p>
      </div>

      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full"></div>
      </div>

      <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 mb-6">
        {{ error }}
      </div>

      <div v-else-if="courses.length === 0 && videos.length === 0" class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-8 text-center">
        <svg class="w-12 h-12 text-learning-text-muted mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <p class="text-learning-text-secondary mb-4">No courses yet. / 尚無課程。</p>
      </div>

      <div v-else-if="courses.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="course in courses"
          :key="course.id"
          @click="goToCourse(course.id)"
          class="bg-learning-surface rounded-xl overflow-hidden border border-learning-bg-tertiary cursor-pointer card-interactive group"
        >
          <div class="relative aspect-video bg-learning-bg-primary">
            <img :src="`https://picsum.photos/seed/${course.id}/640/360`" :alt="course.title" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
            <div v-if="getCourseProgress(course) > 0" class="absolute top-3 right-3 px-2 py-1 bg-black/70 rounded text-xs text-white font-medium">
              {{ getCourseProgress(course) }}% complete / 完成
            </div>
          </div>
          <div class="p-5">
            <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-2">
              {{ course.title }}
            </h3>
            <p class="text-learning-text-secondary text-sm mb-4">
              {{ course.description || 'No description / 無描述' }}
            </p>
            <div class="flex items-center gap-4 text-sm text-learning-text-muted">
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {{ getVideoCount(course) }} videos / 影片
              </span>
            </div>

            <div v-if="getCourseProgress(course) > 0" class="mt-4">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-learning-text-secondary">Progress / 進度</span>
                <span class="text-learning-text-primary">{{ getCourseProgress(course) }}%</span>
              </div>
              <div class="h-1.5 bg-learning-bg-primary rounded-full overflow-hidden">
                <div
                  class="h-full bg-learning-accent-primary rounded-full transition-all"
                  :style="{ width: `${getCourseProgress(course)}%` }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="videos.length > 0" class="mb-6">
        <h2 class="text-xl font-semibold font-display text-learning-text-primary mb-4">Available Videos / 可用影片</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="video in videos"
            :key="video.id"
            @click="goToVideo(video.id)"
            class="bg-learning-surface rounded-xl overflow-hidden border border-learning-bg-tertiary cursor-pointer card-interactive group"
          >
            <div class="relative aspect-video bg-learning-bg-primary">
              <img :src="video.thumbnail || `https://picsum.photos/seed/${video.id}/640/360`" :alt="video.title" class="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
              <div class="absolute top-3 right-3 px-2 py-1 bg-black/70 rounded text-xs text-white font-medium">
                {{ formatDuration(video.duration) }}
              </div>
              <div v-if="video.status === 'ready'" class="absolute bottom-3 left-3 px-2 py-1 bg-green-500/80 rounded text-xs text-white">
                Ready / 就緒
              </div>
              <div v-else class="absolute bottom-3 left-3 px-2 py-1 bg-yellow-500/80 rounded text-xs text-white">
                {{ video.status }}
              </div>
            </div>
            <div class="p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-2 line-clamp-2">
                {{ video.title }}
              </h3>
              <p class="text-learning-text-secondary text-sm mb-4 line-clamp-3">
                {{ video.study_plan_notes || video.description || 'No description / 無描述' }}
              </p>
              <p v-if="video.study_plan_notes && video.study_plan_notes_zh" class="text-learning-accent-secondary text-sm mb-4 line-clamp-3">
                {{ video.study_plan_notes_zh }}
              </p>
              <div class="flex items-center gap-2 text-sm text-learning-text-muted">
                <span v-if="video.uploader" class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ video.uploader }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>