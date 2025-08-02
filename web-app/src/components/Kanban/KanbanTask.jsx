import React from 'react';
import { useDrag } from 'react-dnd';
import { Calendar, User, Trash2, Tag, DollarSign } from 'lucide-react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

const KanbanTask = ({ task, onDelete }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'task',
    item: { id: task?.id, column_id: task?.column_id },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

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

  return (
    <div
      ref={drag}
      className={`p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border cursor-move transition-all duration-200 ${
        isDragging ? 'opacity-50 scale-95' : 'hover:shadow-md'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-medium text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
          {task.title}
        </h4>
        <div className="flex gap-1">
          {task.priority && (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
              {task.priority === 'high' ? 'Высокий' : task.priority === 'medium' ? 'Средний' : 'Низкий'}
            </span>
          )}
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(task.id);
              }}
              className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              title="Удалить задачу"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          )}
        </div>
      </div>

      {task.description && (
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Теги */}
      {task.tags && task.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {task.tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full text-xs font-medium flex items-center gap-1"
            >
              <Tag className="h-3 w-3" />
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Бюджет */}
      {task.budget && (
        <div className="flex items-center gap-1 mb-3 text-xs text-gray-600 dark:text-gray-400">
          <DollarSign className="h-3 w-3" />
          <span>{task.budget.toLocaleString('ru-RU')} ₽</span>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
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
};

export default KanbanTask; 