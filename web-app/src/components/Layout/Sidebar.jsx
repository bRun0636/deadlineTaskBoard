import React from 'react';
import { NavLink } from 'react-router-dom';
import { X, Home, Layout, User, Shield, Package } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

const Sidebar = ({ open, setOpen }) => {
  const { user, isAdmin } = useAuth();

  const navigation = [
    { name: 'Дашборд', href: '/dashboard', icon: Home },
    { name: 'Мои доски', href: '/boards', icon: Layout },
    { name: 'Публичные доски', href: '/public-boards', icon: Layout },
    { name: 'Заказы', href: '/orders', icon: Package },
    { name: 'Профиль', href: '/profile', icon: User },
  ];

  const adminNavigation = [
    { name: 'Админ панель', href: '/admin', icon: Shield },
  ];

  const allNavigation = isAdmin ? [...navigation, ...adminNavigation] : navigation;

  return (
    <>
      {/* Мобильное меню */}
      <div
        className={`fixed inset-0 z-50 lg:hidden ${
          open ? 'block' : 'hidden'
        }`}
      >
        <div className="fixed inset-0 bg-gray-900/80" onClick={() => setOpen(false)} />
        
        <div className="fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-gray-800">
          <div className="flex h-full flex-col">
            <div className="flex h-16 shrink-0 items-center border-b border-gray-200 px-6 dark:border-gray-700">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Deadline Task Board
              </h1>
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-700 lg:hidden dark:text-gray-300"
                onClick={() => setOpen(false)}
              >
                <span className="sr-only">Закрыть меню</span>
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <nav className="flex flex-1 flex-col">
              <ul className="flex flex-1 flex-col gap-y-7 px-6 py-4">
                <li>
                  <ul className="-mx-2 space-y-1">
                    {allNavigation.map((item) => (
                      <li key={item.name}>
                        <NavLink
                          to={item.href}
                          className={({ isActive }) =>
                            `group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                              isActive
                                ? 'bg-primary-600 text-white'
                                : 'text-gray-700 hover:text-primary-600 hover:bg-primary-50 dark:text-gray-300 dark:hover:text-primary-400 dark:hover:bg-gray-700'
                            }`
                          }
                          onClick={() => setOpen(false)}
                        >
                          <item.icon className="h-6 w-6 shrink-0" />
                          {item.name}
                        </NavLink>
                      </li>
                    ))}
                  </ul>
                </li>
                
                <li className="mt-auto">
                  <div className="flex items-center gap-x-4 px-6 py-3 text-sm font-semibold leading-6 text-gray-900 dark:text-gray-100">
                    <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <span className="sr-only">Ваш профиль</span>
                    <span aria-hidden="true">{user?.full_name || user?.username}</span>
                  </div>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>

      {/* Десктопное меню */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white px-6 pb-4 dark:border-gray-700 dark:bg-gray-800">
          <div className="flex h-16 shrink-0 items-center">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Deadline Task Board
            </h1>
          </div>
          
          <nav className="flex flex-1 flex-col">
            <ul className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul className="-mx-2 space-y-1">
                  {allNavigation.map((item) => (
                    <li key={item.name}>
                      <NavLink
                        to={item.href}
                        className={({ isActive }) =>
                          `group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                            isActive
                              ? 'bg-primary-600 text-white'
                              : 'text-gray-700 hover:text-primary-600 hover:bg-primary-50 dark:text-gray-300 dark:hover:text-primary-400 dark:hover:bg-gray-700'
                          }`
                        }
                      >
                        <item.icon className="h-6 w-6 shrink-0" />
                        {item.name}
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </li>
              
              <li className="mt-auto">
                <div className="flex items-center gap-x-4 px-6 py-3 text-sm font-semibold leading-6 text-gray-900 dark:text-gray-100">
                  <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                    <User className="h-5 w-5 text-white" />
                  </div>
                  <span className="sr-only">Ваш профиль</span>
                  <span aria-hidden="true">{user?.full_name || user?.username}</span>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </>
  );
};

export default Sidebar; 