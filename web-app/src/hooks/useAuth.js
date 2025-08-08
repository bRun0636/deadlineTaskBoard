import { useState, useEffect, createContext, useContext } from 'react';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const response = await authAPI.me();
        setUser(response);
      }
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      const { access_token, user: userData } = response;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      toast.success('Успешный вход!');
      return userData;
    } catch (error) {
      console.error('Login error details:', error);
      
      // Более детальная обработка ошибок
      let errorMessage = 'Ошибка входа';
      
      if (error.response?.status === 401) {
        errorMessage = 'Неверное имя пользователя или пароль';
      } else if (error.response?.status === 422) {
        errorMessage = 'Некорректные данные для входа';
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
      
      toast.error(errorMessage, {
        duration: 5000, // Показываем ошибку дольше
        position: 'top-center'
      });
      
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      toast.success('Регистрация успешна! Теперь войдите в систему.');
      return response;
    } catch (error) {
      console.error('Register error details:', error);
      
      // Более детальная обработка ошибок регистрации
      let errorMessage = 'Ошибка регистрации';
      
      if (error.response?.status === 400) {
        errorMessage = 'Некорректные данные для регистрации';
      } else if (error.response?.status === 409) {
        errorMessage = 'Пользователь с таким именем или email уже существует';
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
      
      toast.error(errorMessage, {
        duration: 5000, // Показываем ошибку дольше
        position: 'top-center'
      });
      
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Вы вышли из системы');
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAdmin: user?.is_superuser || false,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 