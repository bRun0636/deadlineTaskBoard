import React from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { Plus, Calendar, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { boardsAPI, tasksAPI } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import BoardCard from '../../components/Board/BoardCard';
import TaskCard from '../../components/Task/TaskCard';
import CreateBoardModal from '../../components/Board/CreateBoardModal';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = React.useState(false);

  const { data: boards, isLoading: boardsLoading } = useQuery(
    'boards',
    () => boardsAPI.getAll(),
    {
      refetchOnWindowFocus: false,
    }
  );

  const { data: myTasks, isLoading: tasksLoading } = useQuery(
    'myTasks',
    () => tasksAPI.getMy({ limit: 5 }),
    {
      refetchOnWindowFocus: false,
    }
  );

  const { data: taskStats, isLoading: statsLoading } = useQuery(
    'taskStats',
    () => tasksAPI.getStats(),
    {
      refetchOnWindowFocus: false,
    }
  );

  const { data: assignedTasks, isLoading: assignedLoading } = useQuery(
    'assignedTasks',
    () => tasksAPI.getAssigned({ limit: 5 }),
    {
      refetchOnWindowFocus: false,
    }
  );

  // Мутация для удаления доски
  const deleteBoardMutation = useMutation(
    (boardId) => boardsAPI.delete(boardId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('boards');
        toast.success('Доска удалена');
      },
      onError: (error) => {
        // Если доска не найдена (404), возможно пользователь находится на странице доски
        if (error.response?.status === 404) {
          toast.error('Доска уже была удалена');
        } else {
          toast.error('Ошибка при удалении доски');
        }
      },
    }
  );

  const stats = [
    {
      name: 'Мои доски',
      value: boards?.length || 0,
      icon: Calendar,
      color: 'text-blue-600',
    },
    {
      name: 'Всего задач',
      value: taskStats?.total_tasks || 0,
      icon: CheckCircle,
      color: 'text-green-600',
    },
    {
      name: 'Назначенные мне',
      value: taskStats?.assigned_tasks || 0,
      icon: Clock,
      color: 'text-yellow-600',
    },
  ];

  // Обработчик удаления доски
  const handleDeleteBoard = (boardId) => {
    const board = boards?.find(b => b.id === boardId);
    if (board && window.confirm(`Вы уверены, что хотите удалить доску "${board.title}"? Это действие нельзя отменить.`)) {
      deleteBoardMutation.mutate(boardId);
    }
  };

  if (boardsLoading || tasksLoading || assignedLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }



  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Добро пожаловать, {user?.full_name || user?.username}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Управляйте своими задачами и проектами
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="h-5 w-5" />
          Создать доску
        </button>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.name} className="card p-6">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg bg-gray-100 dark:bg-gray-700`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  {stat.name}
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  {stat.value}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Мои доски */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Мои доски
          </h2>
          <Link
            to="/boards"
            className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400"
          >
            Посмотреть все
          </Link>
        </div>
        
        {boards?.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {boards.slice(0, 6).map((board) => (
              <BoardCard key={board.id} board={board} onDelete={handleDeleteBoard} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
              Нет досок
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Создайте свою первую доску для начала работы
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn btn-primary"
              >
                Создать доску
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Мои задачи */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Созданные мной
          </h2>
          {myTasks?.length > 0 ? (
            <div className="space-y-3">
              {myTasks.map((task) => (
                <TaskCard key={task.id} task={task} compact />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                У вас пока нет созданных задач
              </p>
            </div>
          )}
        </div>

        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Назначенные мне
          </h2>
          {assignedTasks?.length > 0 ? (
            <div className="space-y-3">
              {assignedTasks.map((task) => (
                <TaskCard key={task.id} task={task} compact />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Вам пока не назначили задач
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Модальное окно создания доски */}
      <CreateBoardModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
};

export default DashboardPage; 