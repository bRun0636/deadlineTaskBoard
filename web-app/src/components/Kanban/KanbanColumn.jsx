import React from 'react';
import { useDrop } from 'react-dnd';
import { Plus, Trash2 } from 'lucide-react';
import KanbanTask from './KanbanTask';


const KanbanColumn = ({ column, onTaskMove, onCreateTask, onDeleteColumn, onDeleteTask }) => {
  const [{ isOver }, drop] = useDrop({
    accept: 'task',
    drop: (item) => {
      if (item.column_id !== column.id) {
        onTaskMove(item.id, column.id);
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

  return (
    <div
      ref={drop}
      className={`rounded-lg p-3 min-h-[400px] border border-gray-300 ${
        isOver ? 'ring-2 ring-primary-500' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
          {column.name}
        </h3>
        <div className="flex gap-1">
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