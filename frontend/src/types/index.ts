export interface Video {
    id: string;
    title: string;
    description: string | null;
    source_type: string;
    youtube_url: string;
    file_path: string | null;
    duration: number;
    chunk_duration: number;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface VideoChunk {
    id: string;
    video_id: string;
    chunk_index: number;
    start_time: number;
    end_time: number;
    duration: number;
    transcript: any[] | null;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface Course {
    id: string;
    title: string;
    description: string | null;
    status: string;
    current_video_index: number;
    created_at: string;
    updated_at: string;
}

export interface Vocabulary {
    id: string;
    word: string;
    definition: string | null;
    context: string | null;
    cefr_level: string | null;
    review_count: number;
    next_review: string | null;
}