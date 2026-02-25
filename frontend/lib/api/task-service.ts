import { Task } from '../types';
import { apiClient } from './client';

export class TaskService {
  // Get all tasks for the authenticated user
  static async getAllTasks(userId: string): Promise<Task[]> {
    try {
      // The backend has task routes under /api/{user_id}/tasks
      const response: any = await apiClient.get(`/${userId}/tasks`);
      // Backend returns TaskListResponse format: { tasks: [...], total, limit, offset }
      return response.tasks.map((task: any) => ({
        id: task.id,
        title: task.title,
        description: task.description,
        completed: task.status === 'completed',
        priority: task.priority,
        userId: userId,
        createdAt: new Date(task.created_at),
        updatedAt: new Date(task.updated_at),
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
        priority: taskData.priority || 'medium',
      });

      // The backend returns a TaskResponse object directly
      // Map the backend response to the frontend Task interface
      return {
        id: response.id,
        title: response.title,
        description: response.description,
        completed: response.status === 'completed',
        priority: response.priority,
        userId: userId, // Use the passed userId
        createdAt: new Date(response.created_at),
        updatedAt: new Date(response.updated_at),
      };
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  }

  // Update an existing task
  static async updateTask(userId: string, taskId: string, taskData: Partial<Task>): Promise<Task> {
    try {
      // Only send allowed fields to the backend (title, description, completed)
      const updatePayload: any = {};
      if (taskData.title !== undefined) updatePayload.title = taskData.title;
      if (taskData.description !== undefined) updatePayload.description = taskData.description;
      if (taskData.completed !== undefined) updatePayload.completed = taskData.completed;

      const response: any = await apiClient.put(`/${userId}/tasks/${taskId}`, updatePayload);

      // The backend returns a TaskResponse object directly
      // Map the backend response to the frontend Task interface
      return {
        id: response.id,
        title: response.title,
        description: response.description,
        completed: response.status === 'completed',
        priority: response.priority,
        userId: userId, // Use the passed userId
        createdAt: new Date(response.created_at),
        updatedAt: new Date(response.updated_at),
      };
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  }

  // Delete a task
  static async deleteTask(userId: string, taskId: string): Promise<void> {
    try {
      // The delete endpoint returns 204 No Content
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

      // The backend returns a TaskResponse object directly
      // Map the backend response to the frontend Task interface
      return {
        id: response.id,
        title: response.title,
        description: response.description,
        completed: response.status === 'completed',
        priority: response.priority,
        userId: userId, // Use the passed userId
        createdAt: new Date(response.created_at),
        updatedAt: new Date(response.updated_at),
      };
    } catch (error) {
      console.error('Error toggling task completion:', error);
      throw error;
    }
  }
}