/**
 * API Client for TaskFlow Backend
 */

import type {
  Task,
  TaskInput,
  Notification,
  SignupInput,
  SigninInput,
  AuthResponse,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

// Token management
let authToken: string | null = null;

export function setAuthToken(token: string) {
  authToken = token;
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

export function getAuthToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== "undefined") {
    authToken = localStorage.getItem("auth_token");
  }
  return authToken;
}

export function clearAuthToken() {
  authToken = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

// Fetch wrapper with auth header
async function fetchWithAuth(
  endpoint: string,
  options: RequestInit = {},
  skipAuthRedirect: boolean = false
): Promise<Response> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized - but NOT for auth endpoints (signin/signup)
    if (response.status === 401 && !skipAuthRedirect) {
      clearAuthToken();
      if (typeof window !== "undefined") {
        window.location.href = "/signin";
      }
    }

    return response;
  } catch (error) {
    // Network error, CORS error, or server unreachable
    console.error("API Request failed:", error);
    throw new Error("Unable to connect to server. Please check your connection.");
  }
}

// Auth API
export const authApi = {
  async signup(data: SignupInput): Promise<AuthResponse> {
    const response = await fetchWithAuth("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }, true); // Skip auth redirect for signup

    if (!response.ok) {
      let errorMessage = "Signup failed";
      try {
        const error = await response.json();
        errorMessage = error.detail || errorMessage;
      } catch {
        errorMessage = `Signup failed (${response.status})`;
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    setAuthToken(result.access_token);
    return result;
  },

  async signin(data: SigninInput): Promise<AuthResponse> {
    const response = await fetchWithAuth("/api/auth/signin", {
      method: "POST",
      body: JSON.stringify(data),
    }, true); // Skip auth redirect for signin

    if (!response.ok) {
      let errorMessage = "Invalid email or password";
      try {
        const error = await response.json();
        errorMessage = error.detail || errorMessage;
      } catch {
        if (response.status !== 401) {
          errorMessage = `Sign in failed (${response.status})`;
        }
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    setAuthToken(result.access_token);
    return result;
  },

  async signout(): Promise<void> {
    clearAuthToken();
    if (typeof window !== "undefined") {
      window.location.href = "/signin";
    }
  },
};

// Tasks API
export const tasksApi = {
  async getAll(params?: {
    status?: string;
    priority?: string;
    tag?: string;
    search?: string;
    sort?: string;
    order?: string;
  }): Promise<Task[]> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });
    }

    const endpoint = `/api/tasks${queryParams.toString() ? `?${queryParams}` : ""}`;
    const response = await fetchWithAuth(endpoint);

    if (!response.ok) {
      throw new Error("Failed to fetch tasks");
    }

    return response.json();
  },

  async getById(id: number): Promise<Task> {
    const response = await fetchWithAuth(`/api/tasks/${id}`);

    if (!response.ok) {
      throw new Error("Failed to fetch task");
    }

    return response.json();
  },

  async create(data: TaskInput): Promise<Task> {
    const response = await fetchWithAuth("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to create task");
    }

    return response.json();
  },

  async update(id: number, data: Partial<TaskInput>): Promise<Task> {
    const response = await fetchWithAuth(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to update task");
    }

    return response.json();
  },

  async delete(id: number): Promise<void> {
    const response = await fetchWithAuth(`/api/tasks/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Failed to delete task");
    }
  },

  async toggleComplete(id: number): Promise<{ current_task: Task; next_task: Task | null }> {
    const response = await fetchWithAuth(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    });

    if (!response.ok) {
      throw new Error("Failed to toggle task completion");
    }

    const result = await response.json();
    return result.data;
  },
};

// Chat API - Uses /api/{user_id}/chat endpoint
export const chatApi = {
  async sendMessage(
    userId: number,
    message: string,
    conversationId?: number
  ): Promise<{ response: string; conversation_id: number; tool_calls: Array<any> }> {
    const response = await fetchWithAuth(`/api/${userId}/chat`, {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Chat failed");
    }

    return response.json();
  },

  async getConversations(userId: number): Promise<Array<{ id: number; created_at: string; updated_at: string }>> {
    const response = await fetchWithAuth(`/api/${userId}/conversations`);

    if (!response.ok) {
      throw new Error("Failed to fetch conversations");
    }

    return response.json();
  },

  async getMessages(
    userId: number,
    conversationId: number
  ): Promise<{ messages: Array<{ role: string; content: string }> }> {
    const response = await fetchWithAuth(`/api/${userId}/conversations/${conversationId}/messages`);

    if (!response.ok) {
      throw new Error("Failed to fetch messages");
    }

    return response.json();
  },
};

// Notifications API
export const notificationsApi = {
  async getAll(read?: boolean): Promise<Notification[]> {
    const endpoint = read !== undefined ? `/api/notifications?read=${read}` : "/api/notifications";
    const response = await fetchWithAuth(endpoint);

    if (!response.ok) {
      throw new Error("Failed to fetch notifications");
    }

    return response.json();
  },

  async markAsRead(id: number): Promise<void> {
    const response = await fetchWithAuth(`/api/notifications/${id}/read`, {
      method: "PATCH",
    });

    if (!response.ok) {
      throw new Error("Failed to mark notification as read");
    }
  },
};
