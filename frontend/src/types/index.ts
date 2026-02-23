export interface User {
  id: number;
  email: string;
  name: string;
  age_range?: string;
  primary_goal: string;
  created_at: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface JournalEntry {
  id: number;
  user_id: number;
  content: string;
  sentiment_score: number | null;
  emotion_label: string | null;
  risk_flag: boolean;
  created_at: string;
}

export interface Medication {
  id: number;
  user_id: number;
  name: string;
  dosage: string | null;
  frequency_per_day: number;
  reminder_time: string | null;
}

export interface MedicationLog {
  id: number;
  medication_id: number;
  user_id: number;
  taken_date: string;
  taken: boolean;
}

export interface MedicationSummary {
  current_streak: number;
  weekly_adherence: number;
}

export interface FitnessLog {
  id: number;
  user_id: number;
  log_date: string;
  activity_completed: boolean;
  steps: number;
  minutes_exercised: number;
  intensity: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface WeeklyFitness {
  total_steps: number;
  total_minutes: number;
  avg_intensity: string;
  days_active: number;
  current_streak: number;
}

export interface MonthlyFitness {
  year: number;
  month: number;
  total_steps: number;
  total_minutes: number;
  days_active: number;
  avg_daily_steps: number;
}

export interface SupportCircle {
  id: number;
  name: string;
  created_by: number;
  created_at: string;
}

export interface CircleMember {
  id: number;
  user_id: number;
  role: 'OWNER' | 'MEMBER';
}

export interface CircleWithMembers extends SupportCircle {
  members: CircleMember[];
}

export interface EncouragementMessage {
  id: number;
  circle_id: number;
  sender_id: number;
  receiver_id: number;
  message: string;
  created_at: string;
}

export interface WeeklyInsights {
  avg_mood: number;
  fitness_correlation: number;
  medication_correlation: number;
  predicted_next_mood: number;
  summary: string;
}

export interface UserStats {
  journal: {
    total_entries: number;
    entries_this_week: number;
  };
  medications: {
    total_medications: number;
    doses_taken_this_week: number;
    current_streak: number;
  };
  fitness: {
    total_logs: number;
    days_active_this_week: number;
    total_steps_this_week: number;
    current_streak: number;
  };
  user: {
    id: number;
    name: string;
    primary_goal: string;
  };
}
