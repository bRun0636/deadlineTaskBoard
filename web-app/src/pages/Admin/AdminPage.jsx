import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Shield, Users, Layout, CheckCircle, Eye, EyeOff, UserCheck, UserX, Trash2 } from 'lucide-react';
import { adminAPI } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

const AdminPage = () => {
  const { isAdmin, user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('stats');



  // Запросы данных (всегда вызываем, но с условной логикой)
  const { data: stats, isLoading: statsLoading } = useQuery(
    'adminStats',
    () => adminAPI.getStats(),
    { 
      refetchOnWindowFocus: false,
      enabled: isAdmin, // Запрос выполняется только если пользователь админ

    }
  );

  const { data: users, isLoading: usersLoading, error: usersError } = useQuery(
    'adminUsers',
    () => adminAPI.getAllUsers(),
    { 
      refetchOnWindowFocus: false,
      enabled: isAdmin,

    }
  );

  const { data: boards, isLoading: boardsLoading, error: boardsError } = useQuery(
    'adminBoards',
    () => adminAPI.getAllBoards(),
    { 
      refetchOnWindowFocus: false,
      enabled: isAdmin,

    }
  );

  const { data: deletedBoards, isLoading: deletedBoardsLoading } = useQuery(
    'adminDeletedBoards',
    () => adminAPI.getDeletedBoards(),
    { 
      refetchOnWindowFocus: false,
      enabled: isAdmin && activeTab === 'deletedBoards'
    }
  );

  // Мутации (всегда вызываем, но с условной логикой)
  const updateUserMutation = useMutation(
    ({ userId, data }) => adminAPI.updateUser(userId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminUsers');
        toast.success('Пользователь обновлен');
      },
      onError: () => {
        toast.error('Ошибка при обновлении пользователя');
      },
    }
  );

  const deleteUserMutation = useMutation(
    (userId) => adminAPI.deleteUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminUsers');
        toast.success('Пользователь удален');
      },
      onError: () => {
        toast.error('Ошибка при удалении пользователя');
      },
    }
  );

  const activateBoardMutation = useMutation(
    (boardId) => adminAPI.activateBoard(boardId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminBoards');
        toast.success('Доска активирована');
      },
      onError: () => {
        toast.error('Ошибка при активации доски');
      },
    }
  );

  const deactivateBoardMutation = useMutation(
    (boardId) => adminAPI.deactivateBoard(boardId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminBoards');
        toast.success('Доска деактивирована');
      },
      onError: () => {
        toast.error('Ошибка при деактивации доски');
      },
    }
  );

  const deleteBoardMutation = useMutation(
    (boardId) => adminAPI.deleteBoard(boardId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminBoards');
        queryClient.invalidateQueries('adminDeletedBoards');
        toast.success('Доска полностью удалена');
      },
      onError: () => {
        toast.error('Ошибка при удалении доски');
      },
    }
  );

  const restoreBoardMutation = useMutation(
    (boardId) => adminAPI.restoreBoard(boardId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('adminBoards');
        queryClient.invalidateQueries('adminDeletedBoards');
        toast.success('Доска восстановлена');
      },
      onError: () => {
        toast.error('Ошибка при восстановлении доски');
      },
    }
  );

  // Проверяем права доступа (после всех хуков)
  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
            Доступ запрещен
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            У вас нет прав для доступа к этой странице
          </p>
        </div>
      </div>
    );
  }

  const handleUserToggle = (user, field) => {
    // Нельзя изменить самого себя
    if (user.id === currentUser?.id) {
      toast.error('Вы не можете изменить свой собственный статус или права');
      return;
    }
    
    // Нельзя изменять права других администраторов
    if (field === 'is_superuser' && user.is_superuser) {
      toast.error('Вы не можете снять права администратора у другого администратора');
      return;
    }
    
    // Нельзя изменять статус других администраторов
    if (field === 'is_active' && user.is_superuser) {
      toast.error('Вы не можете изменять статус другого администратора');
      return;
    }
    
    const newValue = !user[field];
    updateUserMutation.mutate({
      userId: user.id,
      data: { [field]: newValue }
    });
  };

  const handleUserDelete = (user) => {
    if (user.id === currentUser?.id) {
      toast.error('Вы не можете удалить свой собственный аккаунт');
      return;
    }
    
    // Нельзя удалить другого администратора
    if (user.is_superuser) {
      toast.error('Вы не можете удалить другого администратора');
      return;
    }
    
    if (window.confirm(`Вы уверены, что хотите удалить пользователя "${user.username}"? Это действие нельзя отменить. Все доски и задачи пользователя будут также удалены.`)) {
      deleteUserMutation.mutate(user.id);
    }
  };

  const handleBoardToggle = (board) => {
    if (board.is_active) {
      deactivateBoardMutation.mutate(board.id);
    } else {
      activateBoardMutation.mutate(board.id);
    }
  };

  const handleBoardDelete = (board) => {
    if (window.confirm(`Вы уверены, что хотите полностью удалить доску "${board.title}"? Это действие нельзя отменить. Все задачи и колонки будут также удалены.`)) {
      deleteBoardMutation.mutate(board.id);
    }
  };

  const handleBoardRestore = (board) => {
    if (window.confirm(`Вы уверены, что хотите восстановить доску "${board.title}"?`)) {
      restoreBoardMutation.mutate(board.id);
    }
  };

  if (statsLoading || usersLoading || boardsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center gap-4">
        <Shield className="h-8 w-8 text-primary-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Панель администратора
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Управление системой и пользователями
          </p>
        </div>
      </div>

      {/* Табы */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'stats', name: 'Статистика', icon: CheckCircle },
            { id: 'users', name: 'Пользователи', icon: Users },
            { id: 'boards', name: 'Доски', icon: Layout },
            { id: 'deletedBoards', name: 'Удаленные доски', icon: Trash2 },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Контент табов */}
      {activeTab === 'stats' && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { name: 'Всего пользователей', value: stats?.total_users || 0, icon: Users, color: 'text-blue-600' },
            { name: 'Активных пользователей', value: stats?.active_users || 0, icon: UserCheck, color: 'text-green-600' },
            { name: 'Всего досок', value: stats?.total_boards || 0, icon: Layout, color: 'text-purple-600' },
            { name: 'Активных досок', value: stats?.active_boards || 0, icon: CheckCircle, color: 'text-green-600' },
            { name: 'Всего задач', value: stats?.total_tasks || 0, icon: CheckCircle, color: 'text-yellow-600' },
            { name: 'Завершенных задач', value: stats?.completed_tasks || 0, icon: CheckCircle, color: 'text-green-600' },
            { name: 'Администраторов', value: stats?.superusers || 0, icon: Shield, color: 'text-red-600' },
          ].map((stat) => (
            <div key={stat.name} className="card p-6">
              <div className="flex items-center">
                <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700">
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
      )}

      {activeTab === 'users' && (
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Управление пользователями
            </h3>
          </div>
          <div className="overflow-x-auto">
            {usersError && (
              <div className="p-6 text-center text-red-500">
                Ошибка загрузки пользователей: {usersError.message}
              </div>
            )}
            {!Array.isArray(users) && !usersError && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Загрузка пользователей...
              </div>
            )}
            {Array.isArray(users) && users.length === 0 && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Пользователи не найдены
              </div>
            )}
            {Array.isArray(users) && users.length > 0 && (
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Пользователь
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Роль
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center">
                          <Users className="h-5 w-5 text-white" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {user.full_name || user.username}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            @{user.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                        {user.is_active ? 'Активен' : 'Неактивен'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.role === 'admin'
                          ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                          : user.role === 'customer'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                          : user.role === 'executor'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                        {user.role === 'admin' ? 'Админ' : 
                         user.role === 'customer' ? 'Заказчик' : 
                         user.role === 'executor' ? 'Исполнитель' : 
                         'Пользователь'}
                      </span>
                    </td>
                                         <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                       <div className="flex gap-2">
                         {user.id !== currentUser?.id && !user.is_superuser && (
                           <>
                             <button
                               onClick={() => handleUserToggle(user, 'is_active')}
                               className={`p-2 rounded-md ${
                                 user.is_active
                                   ? 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
                                   : 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
                               }`}
                               title={user.is_active ? 'Деактивировать' : 'Активировать'}
                             >
                               {user.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                             </button>
                             <button
                               onClick={() => handleUserToggle(user, 'is_superuser')}
                               className={`p-2 rounded-md ${
                                 user.is_superuser
                                   ? 'text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                                   : 'text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20'
                               }`}
                               title={user.is_superuser ? 'Убрать права админа' : 'Назначить админом'}
                             >
                               <Shield className="h-4 w-4" />
                             </button>
                             <button
                               onClick={() => handleUserDelete(user)}
                               className="p-2 rounded-md text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                               title="Удалить пользователя"
                             >
                               <Trash2 className="h-4 w-4" />
                             </button>
                           </>
                         )}
                         {user.id !== currentUser?.id && user.is_superuser && (
                           <span className="text-sm text-gray-500 dark:text-gray-400 px-2 py-1">
                             Админ
                           </span>
                         )}
                         {user.id === currentUser?.id && (
                           <span className="text-sm text-gray-500 dark:text-gray-400 px-2 py-1">
                             Вы
                           </span>
                         )}
                       </div>
                     </td>
                  </tr>
                ))}
              </tbody>
            </table>
            )}
          </div>
        </div>
      )}

      {activeTab === 'boards' && (
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Управление досками
            </h3>
          </div>
          <div className="overflow-x-auto">
            {boardsError && (
              <div className="p-6 text-center text-red-500">
                Ошибка загрузки досок: {boardsError.message}
              </div>
            )}
            {!Array.isArray(boards) && !boardsError && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Загрузка досок...
              </div>
            )}
            {Array.isArray(boards) && boards.length === 0 && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Доски не найдены
              </div>
            )}
            {Array.isArray(boards) && boards.length > 0 && (
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Доска
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Владелец
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {boards.map((board) => (
                  <tr key={board.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center">
                          <Layout className="h-5 w-5 text-white" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {board.title}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {board.description}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {board.owner?.full_name || board.owner?.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        board.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                        {board.is_active ? 'Активна' : 'Неактивна'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleBoardToggle(board)}
                          className={`p-2 rounded-md ${
                            board.is_active
                              ? 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
                              : 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
                          }`}
                          title={board.is_active ? 'Деактивировать' : 'Активировать'}
                        >
                          {board.is_active ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                        <button
                          onClick={() => handleBoardDelete(board)}
                          className="p-2 rounded-md text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                          title="Полностью удалить"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            )}
          </div>
        </div>
      )}

      {activeTab === 'deletedBoards' && (
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Удаленные доски
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Просмотр и восстановление удаленных досок
            </p>
          </div>
          <div className="overflow-x-auto">
            {deletedBoardsLoading && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Загрузка удаленных досок...
              </div>
            )}
            {!Array.isArray(deletedBoards) && !deletedBoardsLoading && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Нет удаленных досок
              </div>
            )}
            {Array.isArray(deletedBoards) && deletedBoards.length === 0 && (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                Удаленные доски не найдены
              </div>
            )}
            {Array.isArray(deletedBoards) && deletedBoards.length > 0 && (
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Доска
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Владелец
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Дата удаления
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {deletedBoards.map((board) => (
                  <tr key={board.id} className="opacity-75">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-gray-400 flex items-center justify-center">
                          <Layout className="h-5 w-5 text-white" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {board.title}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {board.description}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {board.owner?.full_name || board.owner?.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(board.updated_at).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleBoardRestore(board)}
                          className="p-2 rounded-md text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
                          title="Восстановить доску"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleBoardDelete(board)}
                          className="p-2 rounded-md text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                          title="Полностью удалить"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage; 