import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, User, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

const TaskCard = ({ task, compact = false }) => {
  // Проверяем, что task - это валидный объект задачи
  if (!task || typeof task !== 'object' || !task.id || task.type || task.loc || task.msg) {
    return null; // Не рендерим объекты ошибок
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'todo':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'review':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'done':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'done':
        return <CheckCircle className="h-4 w-4" />;
      case 'in_progress':
        return <Clock className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (compact) {
    return (
      <div className="p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm text-gray-900 dark:text-gray-100 truncate">
              {task.title}
            </h4>
            {task.description && (
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                {task.description}
              </p>
            )}
          </div>
          <div className="flex items-center gap-1 ml-2">
            {task.priority && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                {task.priority === 'high' ? 'В' : task.priority === 'medium' ? 'С' : 'Н'}
              </span>
            )}
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
              {getStatusIcon(task.status)}
            </span>
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>
              {task.due_date ? format(new Date(task.due_date), 'dd MMM', { locale: ru }) : 'Без срока'}
            </span>
          </div>
          
          {task.assigned_to && (
            <div className="flex items-center gap-1">
              <User className="h-3 w-3" />
              <span>{task.assigned_to.username}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <Link
      to={`/task/${task.id}`}
      className="block p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border hover:shadow-md transition-shadow duration-200"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
          {task.title}
        </h3>
          {task.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
              {task.description}
            </p>
          )}
        </div>
        
        <div className="flex items-center gap-2 ml-4">
          {task.priority && (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
              {task.priority === 'high' ? 'Высокий' : task.priority === 'medium' ? 'Средний' : 'Низкий'}
          </span>
          )}
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
            {getStatusIcon(task.status)}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <span>
              {task.due_date ? format(new Date(task.due_date), 'dd MMM yyyy', { locale: ru }) : 'Без срока'}
            </span>
            </div>
          
          {task.assigned_to && (
            <div className="flex items-center gap-1">
              <User className="h-4 w-4" />
              <span>{task.assigned_to.username}</span>
            </div>
          )}
        </div>

        <div className="text-xs text-gray-400">
          {task.created_at && format(new Date(task.created_at), 'dd MMM', { locale: ru })}
          </div>
      </div>
    </Link>
  );
};

export default TaskCard; 