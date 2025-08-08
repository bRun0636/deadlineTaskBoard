// Утилиты для предотвращения перезагрузки страницы при ошибках в формах

export const preventPageReload = (event) => {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  return false;
};

export const safeFormSubmit = (submitHandler) => {
  return async (event) => {
    try {
      preventPageReload(event);
      
      // Дополнительная защита от перезагрузки
      const originalLocation = window.location.href;
      
      await submitHandler(event);
      
      // Проверяем, не изменился ли URL (что может указывать на перезагрузку)
      setTimeout(() => {
        if (window.location.href !== originalLocation) {
          console.warn('URL changed during form submission, preventing reload');
          window.history.replaceState({}, document.title, originalLocation);
        }
      }, 50);
      
    } catch (error) {
      console.error('Form submission error:', error);
      preventPageReload(event);
      
      // Дополнительная защита от перезагрузки
      setTimeout(() => {
        const currentPath = window.location.pathname;
        const isAuthPage = currentPath === '/login' || currentPath === '/register';
        
        // Если мы на странице аутентификации и произошла ошибка, 
        // убеждаемся что мы остаемся на этой странице
        if (isAuthPage) {
          window.history.replaceState({}, document.title, currentPath);
        }
      }, 100);
    }
  };
};

export const handleFormError = (error, defaultMessage = 'Произошла ошибка') => {
  console.error('Form error:', error);
  
  let errorMessage = defaultMessage;
  
  if (error.response?.status === 401) {
    errorMessage = 'Неверные учетные данные';
  } else if (error.response?.status === 422) {
    errorMessage = 'Некорректные данные';
  } else if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') {
      errorMessage = detail;
    } else if (Array.isArray(detail)) {
      errorMessage = detail.map(e => e.msg).join(', ');
    } else if (typeof detail === 'object') {
      errorMessage = Object.values(detail).join(', ');
    }
  } else if (error.message) {
    errorMessage = error.message;
  }
  
  return errorMessage;
}; 