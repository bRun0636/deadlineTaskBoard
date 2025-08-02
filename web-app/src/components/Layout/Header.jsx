import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Menu, Bell, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Header = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm dark:border-gray-700 dark:bg-gray-800 sm:gap-x-6 sm:px-6 lg:px-8">
      <button
        type="button"
        className="-m-2.5 p-2.5 text-gray-700 lg:hidden dark:text-gray-300"
        onClick={onMenuClick}
      >
        <span className="sr-only">Открыть меню</span>
        <Menu className="h-6 w-6" />
      </button>

      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="flex flex-1"></div>
        
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-400 hover:text-gray-500 dark:text-gray-300 dark:hover:text-gray-200"
          >
            <span className="sr-only">Уведомления</span>
            <Bell className="h-6 w-6" />
          </button>

          <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200 dark:bg-gray-700" />

          <div className="relative">
            <button
              type="button"
              className="-m-1.5 flex items-center p-1.5 text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500"
              onClick={() => navigate('/profile')}
            >
              <span className="sr-only">Открыть меню пользователя</span>
              <div className="flex items-center">
                <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                  <User className="h-5 w-5 text-white" />
                </div>
                <span className="ml-3 hidden text-sm font-semibold leading-6 text-gray-900 dark:text-gray-100 lg:block">
                  {user?.full_name || user?.username}
                </span>
              </div>
            </button>
          </div>

          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            Выйти
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 