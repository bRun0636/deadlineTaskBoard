import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-gray-300 dark:text-gray-700">404</h1>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Страница не найдена
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Запрашиваемая страница не существует или была перемещена.
          </p>
        </div>

        <div className="space-y-4">
          <Link
            to="/app/dashboard"
            className="btn btn-primary flex items-center justify-center gap-2 w-full"
          >
            <Home className="h-5 w-5" />
            Вернуться на дашборд
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="btn btn-secondary flex items-center justify-center gap-2 w-full"
          >
            <ArrowLeft className="h-5 w-5" />
            Назад
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage; 