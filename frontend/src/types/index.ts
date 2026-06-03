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
    thumbnail?: string;
    uploader?: string;
    created_at: string;
    updated_at: string;
}

export interface CourseVideo {
    id: string;
    course_id: string;
    video_id: string;
    order_index: number;
    video?: Video;
    study_plan?: StudyPlan | null;
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
    course_videos: CourseVideo[];
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

export interface TranscriptSegment {
    start: number;
    end: number;
    text: string;
}

export interface Transcript {
    id: string;
    video_id: string;
    type: 'user' | 'youtube_author' | 'whisper' | 'youtube_auto';
    language: string;
    segments: TranscriptSegment[];
    created_at: string;
}

export interface StudyObjective {
    id: string;
    title: string;
    description: string;
    completed: boolean;
    type: 'vocabulary' | 'grammar' | 'pronunciation' | 'listening' | 'speaking';
}

export interface StudyPlan {
    id: string;
    video_id: string;
    chunk_index: number;
    objectives: StudyObjective[];
    vocabulary: VocabularyItem[];
    grammar: GrammarItem[];
    totalChunks: number;
    completedChunks: number;
    estimatedMinutes: number;
    created_at: string;
}

export interface StudyPlanDisplay {
    objectives: StudyObjective[];
    totalChunks: number;
    completedChunks: number;
    estimatedMinutes: number;
}

export interface VocabularyItem {
    word: string;
    definition: string;
    context: string;
    cefr_level: string;
    pronunciation?: string;
    examples?: string[];
}

export interface GrammarItem {
    pattern: string;
    explanation: string;
    examples: string[];
}