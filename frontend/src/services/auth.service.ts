// Authentication service
import api from './api';
import { LoginRequest, RegisterRequest, Token, User } from '../types';

export const authService = {
  async login(data: LoginRequest): Promise<Token> {
    const response = await api.post('/auth/login', data);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async refreshToken(): Promise<Token> {
    const response = await api.post('/auth/refresh');
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('token');
  },

  setToken(token: string): void {
    localStorage.setItem('token', token);
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },
};

export default authService;
