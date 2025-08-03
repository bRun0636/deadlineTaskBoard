import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Аутентификация
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  me: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Пользователи
export const usersAPI = {
  getAll: async (params) => {
    const response = await api.get('/users', { params });
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/users/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },
};

// Доски
export const boardsAPI = {
  getAll: async (params) => {
    const response = await api.get('/boards', { params });
    return response.data;
  },
  getPublic: async (params) => {
    const response = await api.get('/boards/public', { params });
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/boards/${id}`);
    return response.data;
  },
  create: (data) => api.post('/boards/', data),
  update: async (id, data) => {
    const response = await api.put(`/boards/${id}`, data);
    return response.data;
  },
  delete: (id) => api.delete(`/boards/${id}`),
};

// Колонки
export const columnsAPI = {
  create: async (data) => {
    const response = await api.post('/columns', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/columns/${id}`, data);
    return response.data;
  },
  reorder: async (columns) => {
    const response = await api.patch('/columns/reorder', columns);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/columns/${id}`);
    return response.data;
  },
  getByBoard: async (boardId, params) => {
    const response = await api.get(`/columns/board/${boardId}`, { params });
    return response.data;
  },
}

// Задачи
export const tasksAPI = {
  getAll: async (params) => {
    const response = await api.get('/tasks', { params });
    return response.data;
  },
  getMy: async (params) => {
    const response = await api.get('/tasks/my', { params });
    return response.data;
  },
  getAssigned: async (params) => {
    const response = await api.get('/tasks/assigned', { params });
    return response.data;
  },
  getByBoard: async (boardId, params) => {
    const response = await api.get(`/tasks/board/${boardId}`, { params });
    return response.data;
  },
  getKanban: async (boardId) => {
    const response = await api.get(`/tasks/board/${boardId}/kanban`);
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/tasks', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/tasks/${id}`, data);
    return response.data;
  },
  updateStatus: async (id, column_id) => {
    const response = await api.patch(`/tasks/${id}/status`, { column_id });
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/tasks/${id}`);
    return response.data;
  },
  getStats: async () => {
    const response = await api.get('/tasks/stats/user');
    return response.data;
  },
};

// Заказы
export const ordersAPI = {
  getAll: async (params) => {
    const response = await api.get('/orders', { params });
    return response.data;
  },
  getOpen: async (params) => {
    const response = await api.get('/orders/open', { params });
    return response.data;
  },
  getMy: async (params) => {
    const response = await api.get('/orders/my', { params });
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/orders/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/orders', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/orders/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/orders/${id}`);
    return response.data;
  },
  complete: async (id) => {
    const response = await api.post(`/orders/${id}/complete`);
    return response.data;
  },
  cancel: async (id) => {
    const response = await api.post(`/orders/${id}/cancel`);
    return response.data;
  },
  restore: async (id) => {
    const response = await api.post(`/orders/${id}/restore`);
    return response.data;
  },
  getStats: async () => {
    const response = await api.get('/orders/stats/my');
    return response.data;
  },
};

// Предложения
export const proposalsAPI = {
  getAll: async (params) => {
    const response = await api.get('/proposals', { params });
    return response.data;
  },
  getMy: async (params) => {
    const response = await api.get('/proposals/my', { params });
    return response.data;
  },
  getPending: async (params) => {
    const response = await api.get('/proposals/pending', { params });
    return response.data;
  },
  getByOrder: async (orderId, params) => {
    const response = await api.get(`/proposals/order/${orderId}`, { params });
    return response.data;
  },
  getById: async (id) => {
    const response = await api.get(`/proposals/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/proposals', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/proposals/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/proposals/${id}`);
    return response.data;
  },
  accept: async (id) => {
    const response = await api.post(`/proposals/${id}/accept`);
    return response.data;
  },
  reject: async (id) => {
    const response = await api.post(`/proposals/${id}/reject`);
    return response.data;
  },
  withdraw: async (id) => {
    const response = await api.post(`/proposals/${id}/withdraw`);
    return response.data;
  },
  getStats: async () => {
    const response = await api.get('/proposals/stats/my');
    return response.data;
  },
};

// Администратор
export const adminAPI = {
  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },
  getAllUsers: async (params) => {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },
  getActiveUsers: async (params) => {
    const response = await api.get('/admin/users/active', { params });
    return response.data;
  },
  updateUser: async (userId, data) => {
    const response = await api.put(`/admin/users/${userId}`, data);
    return response.data;
  },
  deleteUser: async (userId) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  },
  getAllBoards: async (params) => {
    const response = await api.get('/admin/boards', { params });
    return response.data;
  },
  getDeletedBoards: async (params) => {
    const response = await api.get('/admin/boards/deleted', { params });
    return response.data;
  },
  getAllBoardsIncludingDeleted: async (params) => {
    const response = await api.get('/admin/boards/all', { params });
    return response.data;
  },
  getBoardById: async (boardId) => {
    const response = await api.get(`/admin/boards/${boardId}`);
    return response.data;
  },
  restoreBoard: async (boardId) => {
    const response = await api.put(`/admin/boards/${boardId}/restore`);
    return response.data;
  },
  activateBoard: async (boardId) => {
    const response = await api.put(`/admin/boards/${boardId}/activate`);
    return response.data;
  },
  deactivateBoard: async (boardId) => {
    const response = await api.put(`/admin/boards/${boardId}/deactivate`);
    return response.data;
  },
  deleteBoard: async (boardId) => {
    const response = await api.delete(`/admin/boards/${boardId}`);
    return response.data;
  },
};

// Сообщения
export const messagesAPI = {
  getByOrder: async (orderId, params) => {
    const response = await api.get(`/messages/order/${orderId}`, { params });
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/messages', data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/messages/${id}`);
    return response.data;
  },
  markAsRead: async (id) => {
    const response = await api.post(`/messages/${id}/read`);
    return response.data;
  },
  markOrderAsRead: async (orderId) => {
    const response = await api.post(`/messages/order/${orderId}/read`);
    return response.data;
  },
  getUnreadCount: async () => {
    const response = await api.get('/messages/unread/count');
    return response.data;
  },
  getOrderUnreadCount: async (orderId) => {
    const response = await api.get(`/messages/order/${orderId}/unread/count`);
    return response.data;
  },
};

export default api; 