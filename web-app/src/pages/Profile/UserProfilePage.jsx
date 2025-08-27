import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { usersAPI } from '../../services/api';
import { User, Mail, Calendar } from 'lucide-react';

const UserProfilePage = () => {
  const { userId } = useParams();
  const { data: user, isLoading, error } = useQuery(['user', userId], () => usersAPI.getById(userId));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Пользователь не найден
        </h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Профиль пользователя
        </h1>
      </div>
      <div className="card p-6 max-w-lg mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <div className="h-16 w-16 rounded-full bg-primary-600 flex items-center justify-center">
            <User className="h-8 w-8 text-white" />
          </div>
                      <div>
              <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">{user.first_name || user.display_name || user.full_name || 'Пользователь'}</div>
              {user.telegram_username && <div className="text-gray-600 dark:text-gray-400">@{user.telegram_username}</div>}
            </div>
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-gray-400" />
            <span>{user.email}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-gray-400" />
            <span>Дата регистрации: {user.created_at ? new Date(user.created_at).toLocaleDateString('ru-RU') : 'Неизвестно'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage; 