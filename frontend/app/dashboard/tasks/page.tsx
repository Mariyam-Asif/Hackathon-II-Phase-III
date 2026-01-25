'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { TaskService } from '../../../lib/api/task-service';
import { Task } from '../../../lib/types';
import { TaskList } from '../../../components/tasks/TaskList';
import { TaskForm } from '../../../components/tasks/TaskForm';

export default function TasksPage() {
  const [session, setSession] = useState<any>(null);

  // Get the user ID from the URL parameter since it's part of the route
  // The session/user context is provided by the parent layout
  const params = useParams();
  const userId = params.user_id as string;
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Load tasks when component mounts
  useEffect(() => {
    if (userId) {
      loadTasks();
    }
  }, [userId]);

  const loadTasks = async () => {
    if (!userId) return;

    try {
      setLoading(true);
      setError(null);
      const userTasks = await TaskService.getAllTasks(userId);
      setTasks(userTasks);
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error loading tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData: Omit<Task, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    if (!userId) return;

    try {
      const newTask = await TaskService.createTask(userId, taskData);
      setTasks([newTask, ...tasks]);
      setShowForm(false);
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    }
  };

  const handleUpdateTask = async (updatedTask: Task) => {
    if (!userId) return;

    try {
      const updated = await TaskService.updateTask(userId, updatedTask.id, {
        title: updatedTask.title,
        description: updatedTask.description,
        completed: updatedTask.completed,
      });

      setTasks(tasks.map(t => t.id === updated.id ? updated : t));
      setEditingTask(null);
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    }
  };

  const handleUpdateTaskForForm = async (taskData: Task | Omit<Task, "id" | "userId" | "createdAt" | "updatedAt">) => {
    if ('id' in taskData) {
      // This is a Task object with an id, so it's an update
      await handleUpdateTask(taskData as Task);
    } else {
      // This shouldn't happen in update context, but for type safety
      console.error('Cannot update task without id');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!userId) return;

    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await TaskService.deleteTask(userId, taskId);
        setTasks(tasks.filter(t => t.id !== taskId));
      } catch (err) {
        setError('Failed to delete task. Please try again.');
        console.error('Error deleting task:', err);
      }
    }
  };

  const handleToggleComplete = async (task: Task) => {
    if (!userId) return;

    try {
      const updated = await TaskService.toggleTaskCompletion(userId, task.id, !task.completed);
      setTasks(tasks.map(t => t.id === task.id ? updated : t));
    } catch (err) {
      setError('Failed to update task status. Please try again.');
      console.error('Error updating task status:', err);
    }
  };

  const startEditing = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const cancelEditing = () => {
    setEditingTask(null);
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="animate-pulse flex flex-col space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {showForm ? 'Cancel' : 'Add New Task'}
            </button>
          </div>

          {error && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          {showForm && (
            <div className="mb-6">
              <TaskForm
                onSubmit={editingTask ? handleUpdateTaskForForm : handleCreateTask}
                onCancel={cancelEditing}
                initialData={editingTask || undefined}
              />
            </div>
          )}

          <TaskList
            tasks={tasks}
            onToggleComplete={handleToggleComplete}
            onStartEdit={startEditing}
            onDelete={handleDeleteTask}
          />
        </div>
      </div>
    </div>
  );
}