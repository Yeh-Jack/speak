import api from './api';
import type { Video, VideoChunk, Transcript } from '@/types';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface StreamChatOptions {
  videoId?: string;
  messages: ChatMessage[];
  systemPrompt?: string;
  onToken?: (token: string, done: boolean) => void;
  onError?: (error: Error) => void;
}

export async function streamChat(options: StreamChatOptions): Promise<void> {
  const { videoId, messages, systemPrompt, onToken, onError } = options;

  let baseUrl = '/api/v1';
  if ((window as any).__API_CONFIG_PROMISE__) {
    await (window as any).__API_CONFIG_PROMISE__;
  }
  if ((window as any).__API_URL__ && (window as any).__API_URL__.includes('://')) {
    baseUrl = `${(window as any).__API_URL__}/api/v1`;
  }

  const response = await fetch(`${baseUrl}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      video_id: videoId || null,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      system_prompt: systemPrompt || null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.error) {
              onError?.(new Error(data.error));
              return;
            }
            onToken?.(data.token || '', data.done || false);
            if (data.done) {
              return;
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export interface StudyPlanResponse {
  id: string;
  video_id: string;
  chunk_index: number | null;
  objectives: Array<{
    id: string;
    title: string;
    description: string;
    completed: boolean;
    type: 'vocabulary' | 'grammar' | 'pronunciation' | 'listening' | 'speaking';
  }>;
  vocabulary: Array<{
    word: string;
    word_zh?: string;
    definition: string;
    definition_zh?: string;
    context: string;
    context_zh?: string;
    cefr_level: string;
    cefr_level_zh?: string;
    pronunciation?: string;
    examples?: string[];
    examples_zh?: string[];
  }>;
  grammar: Array<{
    pattern: string;
    pattern_zh?: string;
    explanation: string;
    explanation_zh?: string;
    examples: string[];
    examples_zh?: string[];
  }>;
  notes: string | null;
  notes_zh?: string | null;
  overall_difficulty: string | null;
  overall_difficulty_zh?: string | null;
  estimated_time: string | null;
  created_at: string | null;
}

export interface VideoResponse {
  video: Video;
  chunks: VideoChunk[];
  transcript?: Transcript;
  study_plan?: StudyPlanResponse;
}

export interface TranscriptResponse {
  segments: Array<{
    start: number;
    end: number;
    text: string;
  }>;
}

export const videoService = {
  async getAllVideos(): Promise<Video[]> {
    const response = await api.get<Video[]>('/videos');
    return response.data;
  },

  async getVideo(id: string): Promise<Video> {
    const response = await api.get<Video>(`/videos/${id}`);
    return response.data;
  },

  async getChunks(videoId: string): Promise<VideoChunk[]> {
    const response = await api.get<VideoChunk[]>(`/videos/${videoId}/chunks`);
    return response.data;
  },

  async getTranscript(videoId: string, type?: string): Promise<Transcript> {
    const url = type ? `/videos/${videoId}/transcripts/${type}` : `/videos/${videoId}/transcripts/whisper`;
    const response = await api.get<Transcript>(url);
    return response.data;
  },

  async getStudyPlans(videoId: string): Promise<StudyPlanResponse[]> {
    const response = await api.get<StudyPlanResponse[]>(`/videos/${videoId}/study-plans`);
    return response.data;
  },

  async getStudyPlan(videoId: string, chunkIndex: number): Promise<StudyPlanResponse> {
    const response = await api.get<StudyPlanResponse>(`/videos/${videoId}/study-plans/${chunkIndex}`);
    return response.data;
  },

  async updateStudyPlanObjective(
    videoId: string,
    chunkIndex: number,
    objectives: Array<{ id: string; completed: boolean }>
  ): Promise<StudyPlanResponse> {
    const response = await api.patch<StudyPlanResponse>(`/videos/${videoId}/study-plans/${chunkIndex}`, {
      objectives,
    });
    return response.data;
  },

  async uploadUserTranscript(
    videoId: string,
    language: string,
    segments: Array<{ start: number; end: number; text: string }>
  ): Promise<Transcript> {
    const response = await api.post<Transcript>(`/videos/${videoId}/transcripts/user`, {
      language,
      segments,
    });
    return response.data;
  },

  async createFromYouTube(youtubeUrl: string, chunkDuration: number = 300): Promise<VideoResponse> {
    const response = await api.post<VideoResponse>('/videos/youtube', { 
      youtube_url: youtubeUrl,
      chunk_duration: chunkDuration,
    });
    return response.data;
  },

  async retryProcessing(videoId: string): Promise<Video> {
    const response = await api.post<Video>(`/videos/${videoId}/retry`);
    return response.data;
  },

  async deleteVideo(id: string): Promise<void> {
    await api.delete(`/videos/${id}`);
  },

  async getAudioUrl(videoId: string, chunkIndex?: number): Promise<string> {
    // Wait for config if needed
    if ((window as any).__API_CONFIG_PROMISE__) {
      await (window as any).__API_CONFIG_PROMISE__;
    }
    const baseUrl = (window as any).__API_URL__ || '';
    const path = chunkIndex !== undefined
      ? `/api/v1/videos/${videoId}/chunks/${chunkIndex}/audio`
      : `/api/v1/videos/${videoId}/audio`;
    return baseUrl ? `${baseUrl}${path}` : path;
  },

  async getStreamUrl(videoId: string): Promise<string> {
    // Wait for config if needed
    if ((window as any).__API_CONFIG_PROMISE__) {
      await (window as any).__API_CONFIG_PROMISE__;
    }
    const baseUrl = (window as any).__API_URL__ || '';
    const path = `/api/v1/videos/${videoId}/stream`;
    return baseUrl ? `${baseUrl}${path}` : path;
  },

  async saveProgress(
    videoId: string,
    chunkIndex: number,
    currentTimestamp: number
  ): Promise<void> {
    await api.patch(`/videos/${videoId}/progress`, {
      chunk_index: chunkIndex,
      current_timestamp: currentTimestamp,
    });
  },

  async getProgress(videoId: string): Promise<{ chunk_index: number; timestamp: number } | null> {
    try {
      const response = await api.get<{ video_id: string; chunk_index: number; timestamp: number }>(
        `/videos/${videoId}/progress`
      );
      return { chunk_index: response.data.chunk_index, timestamp: response.data.timestamp };
    } catch {
      return null;
    }
  },

  async reviewVocabulary(word: string, quality: number = 4): Promise<void> {
    await api.post(`/vocabulary/${encodeURIComponent(word)}/review`, { quality });
  },

  async getReviewedVocabulary(): Promise<string[]> {
    const response = await api.get<string[]>('/vocabulary/reviewed');
    return response.data;
  },

  async getFavoriteVocabulary(): Promise<string[]> {
    const response = await api.get<{ words: string[] }>('/vocabulary/favorites');
    return response.data.words;
  },

  async toggleFavoriteVocabulary(word: string): Promise<void> {
    await api.post(`/vocabulary/favorites/${encodeURIComponent(word)}/toggle`);
  },
};

export default videoService;