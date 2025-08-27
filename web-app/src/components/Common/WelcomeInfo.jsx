import React, { useState, useEffect } from 'react';
import { publicAPI } from '../../services/api';

const WelcomeInfo = () => {
  const [systemInfo, setSystemInfo] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [info, stats] = await Promise.all([
          publicAPI.getSystemInfo(),
          publicAPI.getSystemStats()
        ]);
        setSystemInfo(info);
        setSystemStats(stats);
      } catch (err) {
        setError('Не удалось загрузить информацию о системе');
        console.error('Error fetching system info:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6 mb-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4 mb-4"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
        <p className="text-red-600 dark:text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-lg p-6 mb-6">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          🚀 {systemInfo?.message || 'Добро пожаловать!'}
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Платформа для фрилансеров и заказчиков
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            ✨ Возможности системы
          </h3>
          <ul className="space-y-2">
            {systemInfo?.features?.map((feature, index) => (
              <li key={index} className="flex items-center text-gray-600 dark:text-gray-300">
                <span className="text-green-500 mr-2">✓</span>
                {feature}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            📊 Статистика
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">Всего пользователей:</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400">
                {systemStats?.total_users || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">Активных:</span>
              <span className="font-semibold text-green-600 dark:text-green-400">
                {systemStats?.active_users || 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-300">Статус:</span>
              <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm">
                {systemStats?.system_status || 'active'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          🎯 Доступные роли
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          {systemInfo?.available_roles?.map((role) => (
            <div key={role} className="flex items-center p-3 bg-gray-50 dark:bg-gray-600 rounded-lg">
              <span className="text-lg mr-3">
                {role === 'executor' ? '👨‍💻' : '👔'}
              </span>
              <div>
                <div className="font-medium text-gray-900 dark:text-white capitalize">
                  {role === 'executor' ? 'Исполнитель' : 'Заказчик'}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {role === 'executor' 
                    ? 'Выполняйте задачи и получайте оплату' 
                    : 'Создавайте задачи и находите исполнителей'
                  }
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 text-center">
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Начните работу прямо сейчас - зарегистрируйтесь или войдите в систему
        </p>
        <div className="flex justify-center space-x-4">
          <div className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-4 py-2 rounded-lg">
            📱 Telegram бот доступен
          </div>
          <div className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-4 py-2 rounded-lg">
            🌐 Веб-версия готова
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeInfo;

