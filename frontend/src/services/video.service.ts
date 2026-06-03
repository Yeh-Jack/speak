import api from './api';
import type { Video, VideoChunk, Transcript, StudyPlan } from '@/types';

export interface VideoResponse {
  video: Video;
  chunks: VideoChunk[];
  transcript: Transcript;
  study_plan: StudyPlan;
}

export interface TranscriptResponse {
  segments: Array<{
    start: number;
    end: number;
    text: string;
  }>;
}

export const videoService = {
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

  async getStudyPlan(videoId: string, chunkIndex: number): Promise<StudyPlan> {
    const response = await api.get<StudyPlan>(`/videos/${videoId}/study-plans/${chunkIndex}`);
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

  async createFromYouTube(url: string): Promise<VideoResponse> {
    const response = await api.post<VideoResponse>('/videos/youtube', { url });
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
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
    if (chunkIndex !== undefined) {
      return `${baseUrl}/api/v1/videos/${videoId}/chunks/${chunkIndex}/audio`;
    }
    return `${baseUrl}/api/v1/videos/${videoId}/audio`;
  },

  async getStreamUrl(videoId: string): Promise<string> {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
    return `${baseUrl}/api/v1/videos/${videoId}/stream`;
  },
};

export default videoService;