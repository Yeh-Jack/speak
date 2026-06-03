<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { courseService } from '@/services/course.service';
import type { Course, CourseVideo } from '@/types';

const route = useRoute();
const router = useRouter();

const courseId = computed(() => route.params.id as string);

const course = ref<Course | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const completedCount = computed(() => {
  if (!course.value?.course_videos) return 0;
  return course.value.course_videos.filter((cv, idx) => idx < course.value!.current_video_index).length;
});

const progress = computed(() => {
  if (!course.value?.course_videos || course.value.course_videos.length === 0) return 0;
  return Math.round((completedCount.value / course.value.course_videos.length) * 100);
});

const videoCount = computed(() => {
  return course.value?.course_videos?.length || 0;
});

function goToVideo(videoId: string) {
  router.push(`/videos/${videoId}`);
}

function goBack() {
  router.push('/courses');
}

function getVideoDuration(video: CourseVideo): string {
  if (!video.video) return '0:00';
  const mins = Math.floor(video.video.duration / 60);
  const secs = video.video.duration % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function isVideoCompleted(videoIndex: number): boolean {
  return videoIndex < (course.value?.current_video_index || 0);
}

async function fetchCourse() {
  isLoading.value = true;
  error.value = null;
  try {
    course.value = await courseService.getCourse(courseId.value);
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load course';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchCourse();
});
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
          <span class="text-learning-text-primary">{{ course?.title || 'Loading...' }}</span>
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
      <div v-if="isLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin w-8 h-8 border-4 border-learning-accent-primary border-t-transparent rounded-full"></div>
      </div>

      <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 mb-6">
        {{ error }}
      </div>

      <template v-else-if="course">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="lg:col-span-2">
            <div class="relative aspect-video bg-learning-bg-secondary rounded-xl overflow-hidden mb-6">
              <img :src="`https://picsum.photos/seed/${course.id}/640/360`" :alt="course.title" class="w-full h-full object-cover opacity-60" />
              <div v-if="course.course_videos && course.course_videos.length > 0" class="absolute inset-0 flex items-center justify-center">
                <div
                  class="w-16 h-16 rounded-full bg-learning-accent-primary/90 flex items-center justify-center cursor-pointer hover:scale-110 transition-transform"
                  @click="goToVideo(course.course_videos[course.current_video_index]?.video_id)"
                >
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
              {{ course.description || 'No description' }}
            </p>

            <div class="flex items-center gap-6 mb-8">
              <span class="flex items-center gap-2 text-sm text-learning-text-secondary">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {{ videoCount }} videos
              </span>
              <span class="flex items-center gap-2 text-sm text-learning-text-secondary">
                <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ completedCount }}/{{ videoCount }} completed
              </span>
            </div>

            <h2 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
              Course Content
            </h2>

            <div v-if="!course.course_videos || course.course_videos.length === 0" class="text-center py-8 text-learning-text-secondary">
              No videos in this course yet.
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="(cv, index) in course.course_videos"
                :key="cv.id"
                @click="goToVideo(cv.video_id)"
                class="flex items-center gap-4 p-4 bg-learning-surface rounded-xl border border-learning-bg-tertiary cursor-pointer hover:border-learning-accent-primary/50 transition-colors group"
                :class="{ 'opacity-60': isVideoCompleted(index) }"
              >
                <div class="relative w-24 h-14 rounded-lg overflow-hidden bg-learning-bg-primary flex-shrink-0">
                  <img
                    :src="cv.video?.thumbnail || `https://picsum.photos/seed/${cv.video_id}/320/180`"
                    :alt="cv.video?.title || 'Video'"
                    class="w-full h-full object-cover"
                  />
                  <div v-if="isVideoCompleted(index)" class="absolute inset-0 bg-green-500/20 flex items-center justify-center">
                    <svg class="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                    </svg>
                  </div>
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm text-learning-text-muted font-mono">{{ index + 1 }}.</span>
                    <h3 class="font-medium text-learning-text-primary truncate group-hover:text-learning-accent-secondary transition-colors">
                      {{ cv.video?.title || `Video ${cv.video_id.slice(0, 8)}` }}
                    </h3>
                  </div>
                  <p class="text-sm text-learning-text-muted">{{ getVideoDuration(cv) }}</p>
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
                  <span class="text-learning-text-primary font-medium">{{ progress }}%</span>
                </div>
                <div class="h-2 bg-learning-bg-primary rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-learning-accent-primary to-learning-accent-secondary rounded-full transition-all"
                    :style="{ width: `${progress}%` }"
                  />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4 text-center">
                <div class="p-3 bg-learning-bg-primary rounded-lg">
                  <p class="text-2xl font-bold text-learning-accent-primary">{{ completedCount }}</p>
                  <p class="text-xs text-learning-text-muted">Completed</p>
                </div>
                <div class="p-3 bg-learning-bg-primary rounded-lg">
                  <p class="text-2xl font-bold text-learning-text-primary">{{ videoCount - completedCount }}</p>
                  <p class="text-xs text-learning-text-muted">Remaining</p>
                </div>
              </div>
            </div>

            <div class="bg-learning-surface rounded-xl border border-learning-bg-tertiary p-5">
              <h3 class="text-lg font-semibold font-display text-learning-text-primary mb-4">
                Continue Learning
              </h3>
              <button
                v-if="course.course_videos && course.course_videos.length > 0 && course.current_video_index < course.course_videos.length"
                @click="goToVideo(course.course_videos[course.current_video_index].video_id)"
                class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white font-medium rounded-lg transition-colors"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
                Resume Learning
              </button>
              <p v-else-if="course.course_videos && course.course_videos.length > 0" class="text-center text-learning-text-secondary text-sm py-4">
                Course completed! Great job!
              </p>
              <p v-else class="text-center text-learning-text-secondary text-sm py-4">
                No videos to learn yet.
              </p>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>