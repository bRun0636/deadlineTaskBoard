import React from 'react';

const FormWrapper = ({ children, onSubmit, ...props }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    try {
      if (onSubmit) {
        onSubmit(e);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      // Предотвращаем перезагрузку страницы при ошибке
      e.preventDefault();
      e.stopPropagation();
    }
    
    return false;
  };

  return (
    <form {...props} onSubmit={handleSubmit}>
      {children}
    </form>
  );
};

export default FormWrapper; 