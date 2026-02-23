import axios from 'axios';
import type { 
  AuthResponse, User, JournalEntry, Medication, 
  MedicationSummary, FitnessLog, WeeklyFitness, MonthlyFitness,
  SupportCircle, CircleWithMembers, EncouragementMessage,
  WeeklyInsights, UserStats 
} from '../types';

const API_URL = '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const register = (data: { email: string; password: string; name: string; age_range: string; primary_goal: string }) =>
  api.post<AuthResponse>('/auth/register', data);

export const login = (data: { email: string; password: string }) =>
  api.post<AuthResponse>('/auth/login', data);

// User
export const getProfile = () => api.get<User>('/users/me');

export const updateProfile = (data: { name?: string; age_range?: string; primary_goal?: string; password?: string }) =>
  api.put<User>('/users/me', data);

export const deleteAccount = () => api.delete('/users/me');

// Journal
export const createJournal = (content: string) =>
  api.post<{ sentiment_score: number; emotion_label: string; risk_flag: boolean }>('/journal', { content });

export const getJournals = (params?: { page?: number; limit?: number; search?: string; start_date?: string; end_date?: string }) =>
  api.get<JournalEntry[]>('/journal', { params });

export const getJournal = (id: number) => api.get<JournalEntry>(`/journal/${id}`);

export const updateJournal = (id: number, content: string) =>
  api.put<JournalEntry>(`/journal/${id}`, { content });

export const deleteJournal = (id: number) => api.delete(`/journal/${id}`);

// Medications
export const createMedication = (data: { name: string; dosage?: string; frequency_per_day?: number; reminder_time?: string }) =>
  api.post<Medication>('/medications', data);

export const getMedications = (params?: { page?: number; limit?: number; search?: string }) =>
  api.get<Medication[]>('/medications', { params });

export const getMedication = (id: number) => api.get<Medication>(`/medications/${id}`);

export const updateMedication = (id: number, data: { name?: string; dosage?: string; frequency_per_day?: number; reminder_time?: string }) =>
  api.put<Medication>(`/medications/${id}`, data);

export const deleteMedication = (id: number) => api.delete(`/medications/${id}`);

export const markMedicationTaken = (id: number, data: { taken_date: string; taken: boolean }) =>
  api.post(`/medications/${id}/taken`, data);

export const getMedicationSummary = () => api.get<MedicationSummary>('/medications/summary');

// Fitness
export const createFitness = (data: { log_date: string; activity_completed?: boolean; steps?: number; minutes_exercised?: number; intensity?: string }) =>
  api.post<FitnessLog>('/fitness', data);

export const getFitnessLogs = (params?: { page?: number; limit?: number; start_date?: string; end_date?: string }) =>
  api.get<FitnessLog[]>('/fitness', { params });

export const getFitnessLog = (id: number) => api.get<FitnessLog>(`/fitness/${id}`);

export const updateFitness = (id: number, data: { log_date?: string; activity_completed?: boolean; steps?: number; minutes_exercised?: number; intensity?: string }) =>
  api.put<FitnessLog>(`/fitness/${id}`, data);

export const deleteFitness = (id: number) => api.delete(`/fitness/${id}`);

export const getWeeklyFitness = () => api.get<WeeklyFitness>('/fitness/weekly');

export const getMonthlyFitness = (year?: number, month?: number) => 
  api.get<MonthlyFitness>('/fitness/monthly', { params: { year, month } });

// Circles
export const createCircle = (name: string) =>
  api.post<SupportCircle>('/circles', { name });

export const getCircles = () => api.get<SupportCircle[]>('/circles');

export const getCircle = (id: number) => api.get<CircleWithMembers>(`/circles/${id}`);

export const updateCircle = (id: number, name: string) =>
  api.put<SupportCircle>(`/circles/${id}`, { name });

export const joinCircle = (id: number) => api.post(`/circles/${id}/join`);

export const leaveCircle = (id: number) => api.post(`/circles/${id}/leave`);

export const getCircleMembers = (id: number) => api.get<CircleWithMembers>(`/circles/${id}/members`);

export const removeCircleMember = (circleId: number, userId: number) => 
  api.delete(`/circles/${circleId}/members/${userId}`);

export const getCircleMessages = (id: number) => api.get<EncouragementMessage[]>(`/circles/${id}/messages`);

export const sendCircleMessage = (id: number, data: { receiver_id: number; message: string }) =>
  api.post<EncouragementMessage>(`/circles/${id}/message`, data);

// Insights
export const getWeeklyInsights = () => api.get<WeeklyInsights>('/insights/weekly');

// Stats
export const getStats = () => api.get<UserStats>('/stats');

// Export
export const exportJournal = (format: string = 'json', start_date?: string, end_date?: string) =>
  api.get('/export/journal', { params: { format, start_date, end_date } });

export const exportMedications = (format: string = 'json') =>
  api.get('/export/medications', { params: { format } });

export const exportFitness = (format: string = 'json', start_date?: string, end_date?: string) =>
  api.get('/export/fitness', { params: { format, start_date, end_date } });

export default api;
