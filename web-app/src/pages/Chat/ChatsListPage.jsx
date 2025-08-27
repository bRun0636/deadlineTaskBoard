import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../../hooks/useAuth';
import { ordersAPI, messagesAPI } from '../../services/api';

const ChatsListPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadChats = useCallback(async () => {
    try {
      setLoading(true);
      
      // Получаем заказы пользователя, где есть чаты
      let orders = [];
      try {
        if (user.role === 'customer') {
          orders = await ordersAPI.getMy();
        } else {
          orders = await ordersAPI.getAll();
        }
      } catch (error) {
        console.error('Error loading orders for chats:', error);
        orders = [];
      }
      
      // Фильтруем заказы, где пользователь может общаться
      const chatOrders = orders.filter(order => {
        if (user.role === 'customer') {
          return order.creator_id === user.id && 
                 (order.status === 'in_progress' || order.status === 'completed');
        } else {
          return order.assigned_executor_id === user.id && 
                 (order.status === 'in_progress' || order.status === 'completed');
        }
      });

      // Получаем информацию о сообщениях для каждого заказа
      const chatsWithMessages = await Promise.all(
        chatOrders.map(async (order) => {
          try {
            const messages = await messagesAPI.getByOrder(order.id);
            const unreadCount = await messagesAPI.getOrderUnreadCount(order.id);
            
            return {
              order,
              lastMessage: messages.length > 0 ? messages[messages.length - 1] : null,
              unreadCount: unreadCount.unread_count || 0,
              totalMessages: messages.length
            };
          } catch (error) {
            console.error(`Ошибка загрузки сообщений для заказа ${order.id}:`, error);
            return {
              order,
              lastMessage: null,
              unreadCount: 0,
              totalMessages: 0
            };
          }
        })
      );

      // Сортируем по последнему сообщению
      chatsWithMessages.sort((a, b) => {
        if (!a.lastMessage && !b.lastMessage) return 0;
        if (!a.lastMessage) return 1;
        if (!b.lastMessage) return -1;
        return new Date(b.lastMessage.created_at) - new Date(a.lastMessage.created_at);
      });

      setChats(chatsWithMessages);
    } catch (error) {
      console.error('Error loading chats:', error);
      toast.error('Ошибка загрузки чатов');
      setChats([]); // Устанавливаем пустой массив при ошибке
    } finally {
      setLoading(false);
    }
  }, [user.role, user.id]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else if (diffInHours < 48) {
      return 'Вчера';
    } else {
      return date.toLocaleDateString('ru-RU');
    }
  };

  const formatBudget = (budget) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB'
    }).format(budget);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'in_progress':
        return 'В работе';
      case 'completed':
        return 'Завершен';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/app/orders')}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Мои чаты</h1>
              <p className="text-gray-600 text-sm">
                {user.role === 'customer' ? 'Общение с исполнителями' : 'Общение с заказчиками'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Список чатов */}
      <div className="flex-1 overflow-y-auto p-6">
        {chats.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Нет активных чатов</h3>
            <p className="text-gray-500">
              У вас пока нет заказов в работе. Чаты появятся, когда заказы перейдут в статус "В работе".
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {chats.map((chat) => (
              <div
                key={chat.order.id}
                onClick={() => navigate(`/chat/${chat.order.id}`)}
                className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 truncate">
                        {chat.order.title}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(chat.order.status)}`}>
                          {getStatusLabel(chat.order.status)}
                        </span>
                        {chat.unreadCount > 0 && (
                          <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                            {chat.unreadCount}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                      <span>Бюджет: {formatBudget(chat.order.budget)}</span>
                      <span>{chat.totalMessages} сообщений</span>
                    </div>

                    {chat.lastMessage ? (
                      <div className="flex items-center justify-between">
                        <p className="text-gray-700 truncate flex-1">
                          {chat.lastMessage.content}
                        </p>
                        <span className="text-xs text-gray-400 ml-2 flex-shrink-0">
                          {formatTime(chat.lastMessage.created_at)}
                        </span>
                      </div>
                    ) : (
                      <p className="text-gray-500 italic">Нет сообщений</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatsListPage; 