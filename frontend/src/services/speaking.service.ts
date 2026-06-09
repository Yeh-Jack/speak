import api from './api';

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  speaker?: string;
}

export interface VideoSegmentsResponse {
  segments: TranscriptSegment[];
  source: string;
}

export interface ComparisonResult {
  video_id: string;
  segment_start: number;
  segment_end: number;
  original_text: string;
  user_text: string;
  similarity_score: number;
  feedback: string;
}

export const speakingService = {
  async getVideoSegments(
    videoId: string,
    source: string = 'whisper'
  ): Promise<VideoSegmentsResponse> {
    const response = await api.get<VideoSegmentsResponse>(
      `/speaking/videos/${videoId}/segments`,
      { params: { source } }
    );
    return response.data;
  },

  async getAudioSegment(
    videoId: string,
    start: number,
    end: number
  ): Promise<{ audio_path: string }> {
    const response = await api.get<{ audio_path: string }>(
      `/speaking/videos/${videoId}/audio-segment`,
      { params: { start, end } }
    );
    return response.data;
  },

  async compareRecording(
    videoId: string,
    start: number,
    end: number,
    audioFile: Blob
  ): Promise<ComparisonResult> {
    const formData = new FormData();
    formData.append('file', audioFile, 'recording.webm');

    const response = await api.post<ComparisonResult>(
      `/speaking/videos/${videoId}/compare?start=${start}&end=${end}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};

export default speakingService;