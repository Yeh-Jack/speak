# Frontend Documentation

Vue 3.5 + TypeScript + Vite frontend for AI-powered English learning platform.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Vue 3.5 (Composition API) |
| Language | TypeScript |
| Build | Vite |
| State | Pinia |
| Router | Vue Router 4 |
| HTTP | Axios |
| Styles | Tailwind CSS |

## Directory Structure

```
frontend/src/
├── components/
│   ├── common/           # BaseButton, BaseInput, LocaleText
│   ├── layout/           # AppHeader
│   ├── video/            # VideoPlayer
│   └── learning/         # VocabularyCard, StudyPlanDisplay, ShadowingMode
├── views/                # DashboardView, VideoPlayerView, SpeakingPracticeView, SettingsView
├── composables/         # useI18n, useAuth
├── services/            # api, video.service, speaking.service, stats.service
├── stores/              # video.store, language.store, stats.store
├── types/               # TypeScript interfaces
├── router/              # Vue Router config
├── App.vue              # Root component
└── main.ts              # Entry point
```

## Views

### DashboardView (`/`)
- Video grid with thumbnails
- Stats cards (words learned, hours, streak, daily goal)
- Add video modal (YouTube URL + chunk duration)
- Quick actions for recent videos

### VideoPlayerView (`/videos/:id`)
- Full video player with custom controls
- Chunk navigation
- Transcript display (priority: user > youtube_author > whisper > youtube_auto)
- Study plan tabs (vocabulary, grammar, objectives)
- Shadowing mode for speaking practice

### SpeakingPracticeView (`/speaking`)
- Segment selection from video transcripts
- Audio playback of original segment
- Recording interface (Web Audio API)
- Speech recognition (Web Speech API)
- Similarity scoring and feedback

### SettingsView (`/settings`)
- Placeholder for future settings

## Components

### VideoPlayer
- HTML5 video with custom controls
- Keyboard shortcuts (Space, Arrow keys, M, F)
- Playback rate (0.5x, 1x, 1.5x, 2x)
- Subtitle overlay with Chinese translation

### VocabularyCard
- Flashcard flip animation
- Word, pronunciation, CEFR level
- Definition (EN/ZH)
- Context sentence
- Save/review actions

### StudyPlanDisplay
- Tabbed interface (vocabulary/grammar/objectives)
- Progress tracking
- CEFR level badges

### ShadowingMode
- Sentence-by-sentence practice
- Microphone recording with waveform
- Real-time speech recognition
- Similarity scoring

### LocaleText
- Bilingual text component (EN/ZH)
- Language toggle via store

## State Management (Pinia)

### videoStore
```typescript
currentVideo, chunks, currentChunkIndex
transcripts (priority: user > youtube_author > whisper > youtube_auto)
studyPlans, vocabularyItems, grammarItems, studyObjectives
savedVocabulary, reviewedVocabulary, favoriteVocabulary
isCreatingVideo, createProgress, createError
```

### languageStore
- `showZh`: boolean for Chinese display toggle

### statsStore
- Dashboard statistics state

## Services

### api (Axios instance)
- Base URL from `VITE_API_URL`
- Request/response interceptors

### videoService
- `getAllVideos()`, `getVideo(id)`, `getChunks(videoId)`
- `getTranscript(videoId, type)`
- `getStudyPlans(videoId)`, `updateStudyPlanObjective()`
- `createFromYouTube(url, chunkDuration)`
- `retryProcessing(videoId)`, `deleteVideo(id)`
- `saveProgress()`, `getProgress()`
- `reviewVocabulary()`, `getReviewedVocabulary()`, `getFavoriteVocabulary()`, `toggleFavoriteVocabulary()`

### speakingService
- `getVideoSegments(videoId, source)`
- `getAudioSegment(videoId, start, end)`
- `compareRecording(videoId, start, end, file)`

### statsService
- `getDashboardStats(dailyGoalMinutes)`

## Composables

### useI18n
- `t(en: string, zh: string)`: Bilingual text helper

### useAuth
- Mock authentication (always authenticated)

## TypeScript Types

```typescript
Video, VideoChunk, Vocabulary, Transcript, TranscriptSegment
StudyPlan, StudyObjective, VocabularyItem, GrammarItem
StudyPlanResponse, VideoResponse
```

## Environment Variables

```bash
VITE_API_URL=http://localhost:8080
VITE_DEFAULT_CHUNK_SIZE=30
VITE_YOUTUBE_DOWNLOAD_QUALITY=720
VITE_YOUTUBE_AUDIO_QUALITY=128k
```

## Routes

| Path | Component |
|------|-----------|
| `/` | DashboardView |
| `/videos/:id` | VideoPlayerView |
| `/speaking` | SpeakingPracticeView |
| `/settings` | SettingsView |
| `/courses` | Redirect to `/` |

## Setup

```bash
nvm use
pnpm install
pnpm dev
```

## Theme Colors (Tailwind)

```javascript
learning.bg.primary: #1a1a2e
learning.bg.secondary: #16213e
learning.bg.tertiary: #0f3460
learning.accent.primary: #e94560
learning.accent.secondary: #00d9ff
learning.accent.tertiary: #f5a623
learning.text.primary: #eaeaea
learning.text.secondary: #94a3b8
learning.chinese: #f5a623
```