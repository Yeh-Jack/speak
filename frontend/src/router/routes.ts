import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
    {
        path: '/',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
    },
    {
        path: '/courses',
        redirect: '/',
    },
    {
        path: '/videos/:id',
        name: 'video-player',
        component: () => import('@/views/VideoPlayerView.vue'),
    },
    
    {
        path: '/settings',
        name: 'settings',
        component: () => import('@/views/SettingsView.vue'),
    },
];