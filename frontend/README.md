# English Learning Frontend

Vue 3.5 + TypeScript + Vite frontend for the AI-powered English education platform.

## Prerequisites

- Node.js v22 (see `.nvmrc`)
- pnpm

## Setup

1. Use correct Node.js version:
```bash
nvm use
```

2. Install dependencies:
```bash
pnpm install
```

3. Set up environment:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Start development server:
```bash
pnpm dev
```

## Docker

The frontend Docker image uses Node.js 22 (see Dockerfile).

## Project Structure

```
src/
├── components/          # Vue components
│   ├── common/           # Button, Input, Modal, etc.
│   ├── layout/          # Header, Sidebar, Footer
│   ├── video/           # VideoPlayer, SubtitleTrack
│   ├── learning/        # VocabularyCard, StudyPlanView
│   ├── speaking/        # AudioRecorder, PronunciationView
│   └── exam/            # QuestionView, ExamTimer
├── views/               # Page components (Vue views)
├── composables/         # Vue composables (replacing React hooks)
├── services/            # API services
├── stores/              # Pinia stores
├── types/               # TypeScript types
├── utils/               # Utility functions
├── router/              # Vue Router configuration
└── App.vue              # Root component
```

## Key Differences from React

- **Components**: `.vue` files with `<template>`, `<script setup>`, `<style>`
- **State Management**: Pinia instead of Zustand/Redux
- **Data Fetching**: Vue Query via `@tanstack/vue-query` or VueUse `useFetch`
- **Router**: Vue Router instead of React Router
- **Composables**: Vue composables instead of React hooks

## Vue 3.5 Features Used

- `<script setup>` syntax
- Composition API
- Reactive refs with `.value`
- Computed properties
- Watch and watchEffect
- Lifecycle hooks (onMounted, etc.)
- DefineProps and DefineEmits macros
