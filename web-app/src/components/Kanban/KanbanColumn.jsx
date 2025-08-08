import React from 'react';
import { useDrop } from 'react-dnd';
import { Plus, Trash2, CheckCircle } from 'lucide-react';
import KanbanTask from './KanbanTask';


const KanbanColumn = ({ column, onTaskMove, onCreateTask, onDeleteColumn, onDeleteTask }) => {
  const [{ isOver }, drop] = useDrop({
    accept: 'task',
    drop: (item) => {
      if (item.column_id !== column.id) {
        onTaskMove(item.id, column.id);
        // Показываем уведомление, если задача перемещена в колонку "Готово"
        if (isDoneColumn) {
          // Уведомление показывается в handleTaskMove в BoardPage
        }
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  // Фильтруем задачи, исключая объекты ошибок
  const filteredTasks = Array.isArray(column.tasks) 
    ? column.tasks.filter(task => 
        task && 
        typeof task === 'object' && 
        task.id && 
        !task.type && 
        !task.loc && 
        !task.msg
      )
    : [];

  // Проверяем, является ли это колонкой "Готово"
  const isDoneColumn = column.name && (
    column.name.toLowerCase().includes('готово') ||
    column.name.toLowerCase().includes('done') ||
    column.name.toLowerCase().includes('заверш')
  );

  return (
    <div
      ref={drop}
      className={`rounded-lg p-3 min-h-[400px] border ${
        isDoneColumn 
          ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
          : 'border-gray-300'
      } ${
        isOver ? 'ring-2 ring-primary-500' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold flex items-center ${
            isDoneColumn 
              ? 'text-green-700 dark:text-green-300' 
              : 'text-gray-900 dark:text-gray-100'
          }`}>
            {isDoneColumn && (
              <CheckCircle className="h-5 w-5 mr-2 flex-shrink-0 text-green-600 dark:text-green-400" />
            )}
            <span className="truncate">{column.name}</span>
          </h3>
          {isDoneColumn && (
            <div className="mt-1">
              <span className="text-xs bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 px-2 py-1 rounded-full">
                Завершенные задачи
              </span>
            </div>
          )}
        </div>
        <div className="flex gap-1 flex-shrink-0">
          <button
            onClick={() => onCreateTask(column.id)}
            className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            title="Добавить задачу"
          >
            <Plus className="h-4 w-4" />
          </button>
          {onDeleteColumn && (
            <button
              onClick={() => onDeleteColumn(column.id)}
              className="p-1 text-gray-500 hover:text-red-500 dark:hover:text-red-400"
              title="Удалить колонку"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      <div className="space-y-1">
        {filteredTasks.map((task) => (
          <KanbanTask 
            key={task.id} 
            task={task} 
            onDelete={onDeleteTask}
          />
        ))}
      </div>
    </div>
  );
};

export default KanbanColumn; 