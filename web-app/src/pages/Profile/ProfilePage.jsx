import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from 'react-query';
import { Star, CheckCircle, Clock } from 'lucide-react';
import { usersAPI } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      username: user?.username || '',
      email: user?.email || '',
      full_name: user?.full_name || '',
    },
  });

  const updateProfileMutation = useMutation(
    (data) => usersAPI.update(user.id, data),
    {
      onSuccess: (updatedUser) => {
        updateUser(updatedUser);
        queryClient.invalidateQueries(['user', user.id]);
        toast.success('Профиль успешно обновлен!');
        setIsEditing(false);
      },
      onError: (error) => {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') {
          toast.error(detail);
        } else if (Array.isArray(detail)) {
          detail.forEach(e => toast.error(e.msg));
        } else if (typeof detail === 'object') {
          toast.error(JSON.stringify(detail));
        } else {
          toast.error('Ошибка при обновлении профиля');
        }
      },
    }
  );

  const onSubmit = (data) => {
    updateProfileMutation.mutate(data);
  };

  const handleCancel = () => {
    reset();
    setIsEditing(false);
  };

  const stats = [
    {
      name: 'Рейтинг',
      value: user?.rating || 0,
      icon: Star,
      color: 'text-yellow-600',
    },
    {
      name: 'Выполнено задач',
      value: user?.completed_tasks || 0,
      icon: CheckCircle,
      color: 'text-green-600',
    },
    {
      name: 'В системе',
      value: user?.created_at ? 'С момента регистрации' : 'Неизвестно',
      icon: Clock,
      color: 'text-blue-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Профиль пользователя
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Управляйте своими настройками и информацией
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Основная информация */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Основная информация
              </h2>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="btn btn-secondary"
              >
                {isEditing ? 'Отмена' : 'Редактировать'}
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Имя пользователя
                  </label>
                  <input
                    {...register('username', { 
                      required: 'Имя пользователя обязательно',
                      minLength: { value: 3, message: 'Минимум 3 символа' }
                    })}
                    type="text"
                    className="input"
                    disabled={!isEditing}
                  />
                  {errors.username && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                      {errors.username.message}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email
                  </label>
                  <input
                    {...register('email', { 
                      required: 'Email обязателен',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Неверный формат email'
                      }
                    })}
                    type="email"
                    className="input"
                    disabled={!isEditing}
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                      {errors.email.message}
                    </p>
                  )}
                </div>
              </div>

              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Полное имя
                </label>
                <input
                  {...register('full_name')}
                  type="text"
                  className="input"
                  disabled={!isEditing}
                />
              </div>

              {isEditing && (
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="btn btn-secondary"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    disabled={updateProfileMutation.isLoading}
                    className="btn btn-primary"
                  >
                    {updateProfileMutation.isLoading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      'Сохранить'
                    )}
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Статистика */}
        <div className="space-y-4">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Статистика
            </h3>
            <div className="space-y-4">
              {stats.map((stat) => (
                <div key={stat.name} className="flex items-center">
                  <div className={`p-2 rounded-lg bg-gray-100 dark:bg-gray-700`}>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      {stat.name}
                    </p>
                    <p className="text-sm text-gray-900 dark:text-gray-100">
                      {stat.value}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Информация об аккаунте
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">ID пользователя:</span>
                <span className="text-gray-900 dark:text-gray-100">{user?.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Статус:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  user?.is_active 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {user?.is_active ? 'Активен' : 'Неактивен'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Дата регистрации:</span>
                <span className="text-gray-900 dark:text-gray-100">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString('ru-RU') : 'Неизвестно'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage; 