import React, { useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';

import { useQuery, useMutation, useQueryClient } from 'react-query';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Settings, ArrowLeft } from 'lucide-react';

import { boardsAPI, tasksAPI, columnsAPI } from '../../services/api';
import KanbanBoard from '../../components/Kanban/KanbanBoard';
import CreateTaskModal from '../../components/Task/CreateTaskModal';
import BoardSettingsModal from '../../components/Board/BoardSettingsModal';
import CreateColumnModal from '../../components/Column/CreateColumnModal';

import toast from 'react-hot-toast';

const BoardPage = () => {
  const { boardId } = useParams();
  const numericBoardId = parseInt(boardId);

  // Состояния для модальных окон
  const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
  const [selectedColumnId, setSelectedColumnId] = useState(null);
  const [showCreateColumnModal, setShowCreateColumnModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  const queryClient = useQueryClient();

  // Получение данных доски
  const { data: board, isLoading: boardLoading } = useQuery(
    ['board', numericBoardId],
    () => boardsAPI.getById(numericBoardId),
    { 
      refetchOnWindowFocus: false,

    }
  );

  // Формируем колонки с задачами
  const columnsFromBoard = useMemo(() => {
    if (!board) return [];

    const columns = Array.isArray(board.columns) ? board.columns : [];
    const tasks = Array.isArray(board.tasks) ? board.tasks : [];

    // Группируем задачи по колонкам
    const tasksByColumnId = {};
    tasks.forEach((task) => {
      if (task.column_id) {
        if (!tasksByColumnId[task.column_id]) {
          tasksByColumnId[task.column_id] = [];
        }
        tasksByColumnId[task.column_id].push(task);
      }
    });

    // Создаем массив колонок с задачами
    return columns.map((col) => ({
      id: col.id,
      name: col.name,
      tasks: tasksByColumnId[col.id] || [],
    }));
  }, [board]);

  // Мутация для обновления статуса задачи
  const updateTaskStatusMutation = useMutation(
    ({ taskId, column_id }) => 
    tasksAPI.updateStatus(taskId, column_id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['board', numericBoardId]);
        toast.success('Статус задачи обновлен');
      },
      onError: (error) => {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') {
          toast.error(detail);
        } else if (Array.isArray(detail)) {
          detail.forEach((e) => toast.error(e.msg));
        } else if (typeof detail === 'object') {
          toast.error(JSON.stringify(detail));
        } else {
          toast.error('Ошибка при обновлении статуса');
        }
      },
    }
  );

  // Мутация для удаления задачи
  const deleteTaskMutation = useMutation(
    (taskId) => tasksAPI.delete(taskId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['board', numericBoardId]);
        toast.success('Задача удалена');
      },
      onError: (error) => {
        toast.error('Ошибка при удалении задачи');
      },
    }
  );

  // Мутация для удаления колонки
  const deleteColumnMutation = useMutation(
    (columnId) => columnsAPI.delete(columnId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['board', numericBoardId]);
        toast.success('Колонка удалена');
      },
      onError: (error) => {
        toast.error('Ошибка при удалении колонки');
      },
    }
  );

  // Мутация для изменения порядка колонок
  const reorderColumnsMutation = useMutation(
    (columns) => columnsAPI.reorder(columns),
    {
      onSuccess: () => {
        // Обновляем кэш только при успешном сохранении
        queryClient.invalidateQueries(['board', numericBoardId]);
        toast.success('Порядок колонок обновлен');
      },
      onError: (error) => {
        toast.error('Ошибка при изменении порядка колонок');
        // При ошибке можно откатить изменения, но пока просто показываем ошибку
      },
    }
  );

  const handleCreateColumn = (data) => {
    
    createColumnMutation.mutate(data);
  };

  const createColumnMutation = useMutation(
    (data) => columnsAPI.create({ ...data, board_id: numericBoardId }),
    {
      onSuccess: (newColumn) => {

        queryClient.invalidateQueries(['board', numericBoardId]);
        toast.success('Колонка успешно создана!');
      },
      onError: (error) => {
        console.error('BoardPage - error creating column:', error);
        toast.error('Ошибка при создании колонки');
      },
    }
  );
  const handleTaskMove = (taskId, column_id) => {
    updateTaskStatusMutation.mutate({ taskId, column_id: column_id });
  };

  const handleDeleteTask = (taskId) => {
    if (window.confirm('Вы уверены, что хотите удалить эту задачу?')) {
      deleteTaskMutation.mutate(taskId);
    }
  };

  const handleDeleteColumn = (columnId) => {
    if (window.confirm('Вы уверены, что хотите удалить эту колонку? Все задачи в ней также будут удалены.')) {
      deleteColumnMutation.mutate(columnId);
    }
  };


  const [pendingReorder, setPendingReorder] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isDragging, setIsDragging] = useState(false);

  const handleColumnReorder = (fromIndex, toIndex) => {
    const newColumns = [...columnsFromBoard];
    const [movedColumn] = newColumns.splice(fromIndex, 1);
    newColumns.splice(toIndex, 0, movedColumn);
    
    // Сохраняем ожидающий реордер
    const reorderedColumns = newColumns.map((column, index) => ({
      id: column.id,
      order: index
    }));
    
    setPendingReorder(reorderedColumns);
  };

  const handleColumnDragStart = () => {
    setIsDragging(true);
  };

  const handleColumnDragEnd = () => {
    setIsDragging(false);
    
    // Отправляем запрос только при завершении перетаскивания
    if (pendingReorder) {
      reorderColumnsMutation.mutate(pendingReorder);
      setPendingReorder(null);
    }
  };

  if (boardLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Доска не найдена
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Запрашиваемая доска не существует или у вас нет к ней доступа.
        </p>
        <Link to="/dashboard" className="btn btn-primary">
          Вернуться на дашборд
        </Link>
      </div>
    );
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="space-y-6">
        {/* Заголовок */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <Link
              to="/dashboard"
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              {boardLoading ? (
                <div className="animate-pulse">
                  <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 mb-2"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                </div>
              ) : (
                <>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {board?.title || 'Без названия'}
                  </h1>
                  {board?.description && (
                    <p className="text-gray-600 dark:text-gray-400">{board.description}</p>
                  )}
                </>
              )}
            </div>
          </div>
          {/* Кнопки */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSettingsModal(true)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              title="Настройки доски"
            >
              <Settings className="h-5 w-5" />
            </button>
            <button
              onClick={() => setShowCreateColumnModal(true)}
              className="ml-4 btn btn-secondary"
            >
              + Добавить колонку
            </button>
          </div>
        </div>

        {/* Канбан доска */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-2">
          <KanbanBoard
            columns={columnsFromBoard}
            onTaskMove={(taskId, column_id) => handleTaskMove(taskId, column_id)}
            boardId={numericBoardId}
            onCreateTask={(columnId) => {
              setSelectedColumnId(columnId);
              setShowCreateTaskModal(true);
            }}
            onDeleteColumn={handleDeleteColumn}
            onDeleteTask={handleDeleteTask}
            onColumnReorder={handleColumnReorder}
            onColumnDragStart={handleColumnDragStart}
            onColumnDragEnd={handleColumnDragEnd}
          />
        </div>

        {/* Модальные окна */}
        <CreateTaskModal
          isOpen={showCreateTaskModal}
          onClose={() => {
            setShowCreateTaskModal(false);
            setSelectedColumnId(null);
          }}
          boardId={numericBoardId}
          columnId={selectedColumnId}
        />

        <BoardSettingsModal
          isOpen={showSettingsModal}
          onClose={() => setShowSettingsModal(false)}
          board={board}
        />

        <CreateColumnModal
          isOpen={showCreateColumnModal}
          onCreate={handleCreateColumn}
          onClose={() => setShowCreateColumnModal(false)}
          boardId={numericBoardId}
        />
      </div>
    </DndProvider>
  );
};

export default BoardPage;