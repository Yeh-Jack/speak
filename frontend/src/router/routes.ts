import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
    {
        path: '/',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
    },
    {
        path: '/courses',
        name: 'courses',
        component: () => import('@/views/CourseListView.vue'),
    },
    {
        path: '/courses/:id',
        name: 'course-detail',
        component: () => import('@/views/CourseDetailView.vue'),
    },
    {
        path: '/videos/:id',
        name: 'video-player',
        component: () => import('@/views/VideoPlayerView.vue'),
    },
    {
        path: '/speaking',
        name: 'speaking-practice',
        component: () => import('@/views/SpeakingPracticeView.vue'),
    },
    {
        path: '/settings',
        name: 'settings',
        component: () => import('@/views/SettingsView.vue'),
    },
];