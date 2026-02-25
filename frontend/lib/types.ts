// Task entity interface
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

// User entity interface (handled by Better Auth)
export interface User {
  id: string;
  email: string;
  name?: string;
}

// Task state model for frontend
export interface TaskState {
  loading: boolean;
  error: string | null;
  tasks: Task[];
  selectedTask: Task | null;
}

// Authentication state model for frontend
export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

// API response interfaces
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}