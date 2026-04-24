import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/courses',
    name: 'courses',
    component: () => import('@/views/CourseListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/courses/:id',
    name: 'course-detail',
    component: () => import('@/views/CourseDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/videos/:id',
    name: 'video-player',
    component: () => import('@/views/VideoPlayerView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/speaking',
    name: 'speaking-practice',
    component: () => import('@/views/SpeakingPracticeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/exams',
    name: 'exams',
    component: () => import('@/views/ExamView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
];
