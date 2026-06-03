import api from './api';
import type { Course } from '@/types';

export const courseService = {
  async getCourses(): Promise<Course[]> {
    const response = await api.get<Course[]>('/courses');
    return response.data;
  },

  async getCourse(id: string): Promise<Course> {
    const response = await api.get<Course>(`/courses/${id}`);
    return response.data;
  },

  async createCourse(data: {
    title: string;
    description?: string;
    video_ids?: string[];
  }): Promise<Course> {
    const response = await api.post<Course>('/courses', data);
    return response.data;
  },

  async updateCourse(
    id: string,
    data: {
      title?: string;
      description?: string;
      status?: string;
      current_video_index?: number;
    }
  ): Promise<Course> {
    const response = await api.patch<Course>(`/courses/${id}`, data);
    return response.data;
  },

  async deleteCourse(id: string): Promise<void> {
    await api.delete(`/courses/${id}`);
  },

  async addVideoToCourse(courseId: string, videoId: string): Promise<void> {
    await api.post(`/courses/${courseId}/videos/${videoId}`);
  },

  async removeVideoFromCourse(courseId: string, videoId: string): Promise<void> {
    await api.delete(`/courses/${courseId}/videos/${videoId}`);
  },

  async reorderVideos(
    courseId: string,
    videoOrders: Record<string, number>
  ): Promise<Course> {
    const response = await api.put<Course>(`/courses/${courseId}/videos/reorder`, {
      video_orders: videoOrders,
    });
    return response.data;
  },
};

export default courseService;