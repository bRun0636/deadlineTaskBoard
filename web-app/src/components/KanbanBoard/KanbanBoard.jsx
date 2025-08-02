import './KanbanBoard.css';
import Column from '../Column/Column';
import { TaskStatus, createTask } from '../../types/dto/TaskDTO';
import { useState, useEffect } from 'react';
import axios from 'axios';

const STATUS_DISPLAY = {
  backlog: 'Бэклог',
  approved: 'К утверждению',
  coding: 'В работе',
  testing: 'Тестирование',
  deployed: 'Готово',
};

const KanbanBoard = ({ isNavbarClosed, boardId }) => {
  const [columns, setColumns] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    axios.get(`/api/v1/tasks/board/${boardId}/kanban`)
      .then(res => {
        setColumns(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Ошибка загрузки задач');
        setLoading(false);
      });
  }, [boardId]);

  const [newColumnTitle, setNewColumnTitle] = useState('');
  const [addingColumn, setAddingColumn] = useState(false);

  const handleMoveTask = (taskId, fromColumnId, toColumnId) => {
    setColumns(prev => {
      const task = prev[fromColumnId].find(t => t.id === taskId);
      if (!task) return prev;

      const updatedTask = { ...task, status: toColumnId };

      return {
        ...prev,
        [fromColumnId]: prev[fromColumnId].filter(t => t.id !== taskId),
        [toColumnId]: [...prev[toColumnId], updatedTask],
      };
    });
  };

  const addNewTask = (columnId, taskData) => {
    const newTask = createTask({
      ...taskData,
      status: columnId,
      date: new Date().toLocaleDateString(),
    });
    setColumns(prev => ({
      ...prev,
      [columnId]: [...prev[columnId], newTask],
    }));
  };

  if (loading) return <div>Загрузка задач...</div>;
  if (error) return <div>{error}</div>;

  // Фильтруем только допустимые статусы
  const allowedStatuses = Object.keys(STATUS_DISPLAY);
  const filteredColumns = allowedStatuses.reduce((acc, status) => {
    acc[status] = columns[status] || [];
    return acc;
  }, {});

  return (
    <div className="kanban-board">
      {Object.entries(filteredColumns).map(([status, tasks]) => (
        <Column
          key={status}
          title={STATUS_DISPLAY[status]}
          tasks={tasks}
          columnId={status}
          onMoveTask={handleMoveTask}
          onAddTask={addNewTask}
        />
      ))}
      {allowedStatuses.every(status => (columns[status] || []).length === 0) && (
        <div style={{textAlign: 'center', width: '100%'}}>Нет задач</div>
      )}
    </div>
  );
};

export default KanbanBoard;
