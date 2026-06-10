# English Learning Frontend

Vue 3.5 + TypeScript + Vite frontend for AI-powered English learning platform.

## Prerequisites

- Node.js v22 (see `.nvmrc`)
- pnpm

## Setup

```bash
nvm use
pnpm install
cp .env.example .env.local
pnpm dev
```

## Docker

Docker image uses Node.js 22 (see Dockerfile).

## Project Structure

```
src/
├── components/
│   ├── common/           # Button, Input, LocaleText
│   ├── layout/           # AppHeader
│   ├── video/            # VideoPlayer
│   └── learning/         # VocabularyCard, StudyPlanDisplay, ShadowingMode
├── views/                # Page components
├── composables/           # useI18n, useAuth
├── services/             # API services
├── stores/               # Pinia stores
├── types/                # TypeScript interfaces
├── router/               # Vue Router
├── App.vue
└── main.ts
```

## Views

- `/` - DashboardView (video list, stats, add video modal)
- `/videos/:id` - VideoPlayerView (player, chunks, transcript, study plan)
- `/speaking` - SpeakingPracticeView (segment practice, recording, scoring)
- `/settings` - SettingsView (placeholder)

## Key Features

- Custom video player with keyboard shortcuts
- Bilingual display (EN/ZH toggle)
- Vocabulary cards with SM-2 spaced repetition
- Shadowing mode with speech recognition
- CEFR level badges (A1-C2)

## Environment Variables

```bash
VITE_API_URL=http://localhost:8080
VITE_DEFAULT_CHUNK_SIZE=30
VITE_YOUTUBE_DOWNLOAD_QUALITY=720
VITE_YOUTUBE_AUDIO_QUALITY=128k
```

## Tech Stack

- Vue 3.5 (Composition API, `<script setup>`)
- TypeScript (strict mode)
- Pinia (state management)
- Vue Router 4
- Axios
- Tailwind CSS