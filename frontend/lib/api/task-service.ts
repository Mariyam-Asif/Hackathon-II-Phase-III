import { Task } from '../types';
import { apiClient } from './client';

export class TaskService {
  // Get all tasks for the authenticated user
  static async getAllTasks(userId: string): Promise<Task[]> {
    try {
      // The backend has task routes under /api/{user_id}/tasks
      const response: any = await apiClient.get(`/${userId}/tasks`);
      return response.tasks.map((task: any) => ({
        ...task,
        createdAt: new Date(task.createdAt),
        updatedAt: new Date(task.updatedAt),
      }));
    } catch (error) {
      console.error('Error fetching tasks:', error);
      throw error;
    }
  }

  // Create a new task
  static async createTask(userId: string, taskData: Omit<Task, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<Task> {
    try {
      const response: any = await apiClient.post(`/${userId}/tasks`, {
        title: taskData.title,
        description: taskData.description,
        completed: taskData.completed || false,
      });

      return {
        ...response.task,
        createdAt: new Date(response.task.createdAt),
        updatedAt: new Date(response.task.updatedAt),
      };
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  }

  // Update an existing task
  static async updateTask(userId: string, taskId: string, taskData: Partial<Task>): Promise<Task> {
    try {
      const response: any = await apiClient.put(`/${userId}/tasks/${taskId}`, taskData);

      return {
        ...response.task,
        createdAt: new Date(response.task.createdAt),
        updatedAt: new Date(response.task.updatedAt),
      };
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  }

  // Delete a task
  static async deleteTask(userId: string, taskId: string): Promise<void> {
    try {
      await apiClient.delete(`/${userId}/tasks/${taskId}`);
    } catch (error) {
      console.error('Error deleting task:', error);
      throw error;
    }
  }

  // Toggle task completion status
  static async toggleTaskCompletion(userId: string, taskId: string, completed: boolean): Promise<Task> {
    try {
      const response: any = await apiClient.patch(`/${userId}/tasks/${taskId}/complete`, {
        completed
      });

      return {
        ...response.task,
        createdAt: new Date(response.task.createdAt),
        updatedAt: new Date(response.task.updatedAt),
      };
    } catch (error) {
      console.error('Error toggling task completion:', error);
      throw error;
    }
  }
}