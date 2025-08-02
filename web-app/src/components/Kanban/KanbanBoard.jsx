import React from 'react';
import { useDrop, useDrag } from 'react-dnd';
import KanbanColumn from './KanbanColumn';

const DraggableColumn = ({ column, index, onTaskMove, onCreateTask, onDeleteColumn, onDeleteTask, onColumnMove, onDragStart, onDragEnd }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'column',
    item: () => {
      onDragStart?.();
      return { id: column.id, index };
    },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
    end: () => {
      onDragEnd?.();
    },
  });

  const [{ isOver }, drop] = useDrop({
    accept: 'column',
    hover: (item, monitor) => {
      if (!monitor.isOver({ shallow: true })) {
        return;
      }
      if (item.index === index) {
        return;
      }
      onColumnMove(item.index, index);
      item.index = index;
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <div
      ref={(node) => drag(drop(node))}
      className={`transition-opacity ${isDragging ? 'opacity-50' : ''} ${isOver ? 'ring-2 ring-blue-500' : ''}`}
    >
      <KanbanColumn
        column={column}
        onTaskMove={onTaskMove}
        onCreateTask={(columnId) => onCreateTask(columnId)}
        onDeleteColumn={onDeleteColumn}
        onDeleteTask={onDeleteTask}
      />
    </div>
  );
};

const KanbanBoard = ({ columns, onTaskMove, onCreateTask, onDeleteColumn, onDeleteTask, onColumnReorder, onColumnDragStart, onColumnDragEnd }) => {
  // Проверка наличия колонок
  if (!columns) {
    return <div>Loading columns...</div>;
  }
  else if (columns.length === 0) {
    return <div>No columns found.</div>;
  }

  const handleColumnMove = (fromIndex, toIndex) => {
    // Обновляем локальное состояние для визуального отображения
    // Реальный реордер будет отправлен только при завершении перетаскивания
    if (onColumnReorder) {
      onColumnReorder(fromIndex, toIndex);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-2">
      {columns.map((column, index) => (
        <DraggableColumn
          key={column.id}
          column={column}
          index={index}
          onTaskMove={onTaskMove}
          onCreateTask={onCreateTask}
          onDeleteColumn={onDeleteColumn}
          onDeleteTask={onDeleteTask}
          onColumnMove={handleColumnMove}
          onDragStart={onColumnDragStart}
          onDragEnd={onColumnDragEnd}
        />
      ))}
    </div>
  );
};

export default KanbanBoard;