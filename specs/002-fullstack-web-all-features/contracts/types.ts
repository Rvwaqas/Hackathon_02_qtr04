/**
 * TypeScript type definitions for Todo Full-Stack API
 * Generated from OpenAPI specification
 *
 * These types should be copied to /phase2/frontend/types/api.ts
 */

// ==================== Core Entity Types ====================

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: Priority;
  tags: string[];
  recurrence: Recurrence | null;
  due_date: string | null; // ISO 8601 date-time
  reminder_offset_minutes: ReminderOffset | null;
  parent_task_id: number | null;
  created_at: string; // ISO 8601 date-time
  updated_at: string; // ISO 8601 date-time
}

export interface Notification {
  id: number;
  user_id: string;
  task_id: number;
  message: string;
  read: boolean;
  created_at: string; // ISO 8601 date-time
}

export interface Recurrence {
  type: RecurrenceType;
  interval: number; // 1-365
  days?: number[]; // For weekly: 1=Monday, 7=Sunday
}

// ==================== Enums ====================

export type Priority = "high" | "medium" | "low" | "none";

export type RecurrenceType = "daily" | "weekly" | "monthly";

export type ReminderOffset = 5 | 15 | 30 | 60;

export type TaskStatus = "all" | "pending" | "completed";

export type SortField = "priority" | "due_date" | "created_at";

export type SortOrder = "asc" | "desc";

// ==================== Input Types (Request Bodies) ====================

export interface TaskInput {
  title: string;
  description?: string | null;
  priority?: Priority;
  tags?: string[];
  recurrence?: Recurrence | null;
  due_date?: string | null; // ISO 8601 date-time
  reminder_offset_minutes?: ReminderOffset | null;
}

export interface NotificationUpdateInput {
  read: boolean;
}

// ==================== Query Parameters ====================

export interface TaskListParams {
  status?: TaskStatus;
  priority?: Priority | "all";
  tag?: string;
  search?: string;
  sort?: SortField;
  order?: SortOrder;
}

export interface NotificationListParams {
  read?: boolean;
}

// ==================== API Response Types ====================

export interface ApiResponse<T> {
  data: T;
  error: null;
}

export interface ApiErrorResponse {
  data: null;
  error: ApiError;
}

export interface ApiError {
  message: string;
  code: string;
}

// Specific response types
export type TaskResponse = ApiResponse<Task>;
export type TaskListResponse = ApiResponse<Task[]>;
export type NotificationResponse = ApiResponse<Notification>;
export type NotificationListResponse = ApiResponse<Notification[]>;

export interface ToggleCompleteResponse {
  data: {
    current_task: Task;
    next_task: Task | null; // Present if task is recurring
  };
  error: null;
}

export interface DeleteResponse {
  data: {
    message: string;
  };
  error: null;
}

// ==================== Frontend-Specific Types ====================

/**
 * Form state for creating/editing tasks
 * Extends TaskInput with UI-specific fields
 */
export interface TaskFormState extends Omit<TaskInput, 'due_date'> {
  due_date: Date | null; // Use native Date for form inputs
}

/**
 * Parsed task with Date objects instead of strings
 * Useful for client-side date manipulation
 */
export interface TaskWithDates extends Omit<Task, 'due_date' | 'created_at' | 'updated_at'> {
  due_date: Date | null;
  created_at: Date;
  updated_at: Date;
}

/**
 * Helper to convert API Task to TaskWithDates
 */
export function parseTaskDates(task: Task): TaskWithDates {
  return {
    ...task,
    due_date: task.due_date ? new Date(task.due_date) : null,
    created_at: new Date(task.created_at),
    updated_at: new Date(task.updated_at),
  };
}

/**
 * Helper to convert TaskFormState to TaskInput
 */
export function taskFormToInput(form: TaskFormState): TaskInput {
  return {
    ...form,
    due_date: form.due_date ? form.due_date.toISOString() : null,
  };
}

// ==================== Validation Schemas (for Zod or similar) ====================

/**
 * Validation constraints (copy to Zod schema)
 */
export const ValidationRules = {
  task: {
    title: {
      minLength: 1,
      maxLength: 200,
    },
    description: {
      maxLength: 2000,
    },
    tags: {
      maxCount: 10,
      maxLength: 30,
    },
  },
  recurrence: {
    interval: {
      min: 1,
      max: 365,
    },
  },
  notification: {
    message: {
      maxLength: 500,
    },
  },
} as const;

// ==================== API Error Codes ====================

/**
 * Standard error codes returned by the API
 */
export enum ApiErrorCode {
  VALIDATION_ERROR = "VALIDATION_ERROR",
  UNAUTHORIZED = "UNAUTHORIZED",
  FORBIDDEN = "FORBIDDEN",
  NOT_FOUND = "NOT_FOUND",
  INTERNAL_ERROR = "INTERNAL_ERROR",
}

// ==================== Helper Types ====================

/**
 * Priority order for sorting (high = 0, none = 3)
 */
export const PriorityOrder: Record<Priority, number> = {
  high: 0,
  medium: 1,
  low: 2,
  none: 3,
};

/**
 * Priority display configuration
 */
export interface PriorityConfig {
  label: string;
  color: string; // Tailwind class
  bgColor: string; // Tailwind class
}

export const PriorityDisplay: Record<Priority, PriorityConfig> = {
  high: {
    label: "High",
    color: "text-red-700",
    bgColor: "bg-red-100",
  },
  medium: {
    label: "Medium",
    color: "text-yellow-700",
    bgColor: "bg-yellow-100",
  },
  low: {
    label: "Low",
    color: "text-blue-700",
    bgColor: "bg-blue-100",
  },
  none: {
    label: "None",
    color: "text-gray-700",
    bgColor: "bg-gray-100",
  },
};

/**
 * Recurrence type display labels
 */
export const RecurrenceTypeDisplay: Record<RecurrenceType, string> = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
};

/**
 * Reminder offset display labels
 */
export const ReminderOffsetDisplay: Record<ReminderOffset, string> = {
  5: "5 minutes before",
  15: "15 minutes before",
  30: "30 minutes before",
  60: "1 hour before",
};

/**
 * Day of week labels for weekly recurrence
 */
export const DayOfWeekLabels: Record<number, string> = {
  1: "Monday",
  2: "Tuesday",
  3: "Wednesday",
  4: "Thursday",
  5: "Friday",
  6: "Saturday",
  7: "Sunday",
};

// ==================== Type Guards ====================

/**
 * Type guard to check if response is an error
 */
export function isApiError(
  response: ApiResponse<unknown> | ApiErrorResponse
): response is ApiErrorResponse {
  return response.error !== null;
}

/**
 * Type guard to check if task is overdue
 */
export function isTaskOverdue(task: Task): boolean {
  if (!task.due_date || task.completed) return false;
  return new Date(task.due_date) < new Date();
}

/**
 * Type guard to check if task is recurring
 */
export function isTaskRecurring(task: Task): boolean {
  return task.recurrence !== null;
}

/**
 * Type guard to check if task has reminder
 */
export function hasReminder(task: Task): boolean {
  return task.reminder_offset_minutes !== null && task.due_date !== null;
}
