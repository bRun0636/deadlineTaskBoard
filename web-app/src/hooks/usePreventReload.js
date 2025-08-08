import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const usePreventReload = () => {
  const location = useLocation();

  useEffect(() => {
    const isAuthPage = location.pathname === '/login' || location.pathname === '/register';
    
    if (!isAuthPage) return;

    const handleBeforeUnload = (event) => {
      // Предотвращаем перезагрузку страницы на страницах аутентификации
      event.preventDefault();
      event.returnValue = '';
      return '';
    };

    const handleKeyDown = (event) => {
      // Предотвращаем перезагрузку при нажатии F5 или Ctrl+R
      if (event.key === 'F5' || (event.ctrlKey && event.key === 'r')) {
        event.preventDefault();
        return false;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [location.pathname]);
}; 