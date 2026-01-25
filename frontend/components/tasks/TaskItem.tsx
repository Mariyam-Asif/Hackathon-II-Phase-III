import { Task } from '../../lib/types';

interface TaskItemProps {
  task: Task;
  onToggleComplete: (task: Task) => void;
  onStartEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

export function TaskItem({ task, onToggleComplete, onStartEdit, onDelete }: TaskItemProps) {
  return (
    <li className="py-4">
      <div className="flex items-center">
        <input
          id={`task-${task.id}`}
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggleComplete(task)}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label
          htmlFor={`task-${task.id}`}
          className={`ml-3 flex-1 min-w-0 ${task.completed ? 'text-gray-500 line-through' : 'text-gray-900'}`}
        >
          <span className={`truncate ${task.completed ? 'text-gray-500' : 'text-gray-900'}`}>
            {task.title}
          </span>
          {task.description && (
            <p className="text-sm text-gray-500 truncate mt-1">{task.description}</p>
          )}
        </label>
        <div className="flex space-x-2 ml-4">
          <button
            onClick={() => onStartEdit(task)}
            className="inline-flex items-center px-2.5 py-0.5 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="inline-flex items-center px-2.5 py-0.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Delete
          </button>
        </div>
      </div>
      <div className="ml-7 mt-1 text-xs text-gray-500">
        Created: {new Date(task.createdAt).toLocaleDateString()}
      </div>
    </li>
  );
}