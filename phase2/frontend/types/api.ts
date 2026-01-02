export type Priority = "high" | "medium" | "low" | "none";

export type RecurrenceType = "daily" | "weekly" | "monthly";

export interface Recurrence {
  type: RecurrenceType;
  interval: number;
  days?: number[]; // For weekly: 1=Monday, 7=Sunday
}

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string | null;
  completed: boolean;
  priority: Priority;
  tags: string[];
  recurrence?: Recurrence | null;
  due_date?: string | null;
  reminder_offset_minutes?: number | null;
  parent_task_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface TaskInput {
  title: string;
  description?: string | null;
  priority?: Priority;
  tags?: string[];
  recurrence?: Recurrence | null;
  due_date?: string | null;
  reminder_offset_minutes?: number | null;
}

export interface Notification {
  id: number;
  user_id: string;
  task_id: number;
  message: string;
  read: boolean;
  created_at: string;
}

export interface ApiResponse<T> {
  data: T;
  error: null;
}

export interface ApiError {
  data: null;
  error: {
    message: string;
    code: string;
  };
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface SignupInput {
  name: string;
  email: string;
  password: string;
}

export interface SigninInput {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
