import api from './api';
import type { Video, VideoChunk, Transcript } from '@/types';

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