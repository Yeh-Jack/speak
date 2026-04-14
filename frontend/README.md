# English Learning Frontend

React + TypeScript + Vite frontend for the AI-powered English education platform.

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
├── components/    # Reusable components
│   ├── common/     # Button, Input, Modal, etc.
│   ├── layout/   # Header, Sidebar, Footer
│   ├── video/    # VideoPlayer, SubtitleTrack
│   ├── learning/ # VocabularyCard, StudyPlanView
│   ├── speaking/ # AudioRecorder, PronunciationView
│   └── exam/     # QuestionView, ExamTimer
├── pages/        # Page components
├── hooks/        # Custom React hooks
├── services/     # API services
├── stores/       # Zustand state management
├── types/        # TypeScript types
├── utils/        # Utility functions
└── constants/    # Constants
```
