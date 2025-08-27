import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../../hooks/useAuth';
import { ordersAPI, messagesAPI } from '../../services/api';

const ChatPage = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [order, setOrder] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [receiverId, setReceiverId] = useState(null);
  const [lastMessageId, setLastMessageId] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadMessages = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      
      const messagesData = await messagesAPI.getByOrder(orderId);
      
      // Проверяем, есть ли новые сообщения
      if (messagesData.length > 0) {
        const latestMessage = messagesData[messagesData.length - 1];
        if (lastMessageId !== latestMessage.id) {
          setMessages(messagesData);
          setLastMessageId(latestMessage.id);
          
          // Показываем уведомление о новом сообщении, если это не наше сообщение
          if (!showLoading && latestMessage.sender_id !== user.id) {
            toast.info('Новое сообщение!', {
              position: "top-right",
              autoClose: 3000,
            });
          }
        }
      } else {
        setMessages(messagesData);
      }
      
    } catch (error) {
      console.error('Ошибка загрузки сообщений:', error);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  }, [orderId, lastMessageId, user.id]);

  const loadOrderAndMessages = useCallback(async () => {
    try {
      setLoading(true);
      
      // Загружаем информацию о заказе
      const orderData = await ordersAPI.getById(orderId);
      setOrder(orderData);
      
      // Определяем получателя на основе роли пользователя
      if (user.role === 'customer') {
        setReceiverId(orderData.assigned_executor_id);
      } else if (user.role === 'executor') {
        setReceiverId(orderData.creator_id);
      }
      
      // Загружаем сообщения
      await loadMessages(true);
      
    } catch (error) {
      toast.error('Ошибка загрузки данных');
      navigate('/app/orders');
    } finally {
      setLoading(false);
    }
  }, [orderId, user.role, navigate, loadMessages]);

  useEffect(() => {
    if (orderId) {
      loadOrderAndMessages();
    }
  }, [orderId, loadOrderAndMessages]);

  // Автоматическое обновление сообщений
  useEffect(() => {
    if (orderId && autoRefresh) {
      const interval = setInterval(() => {
        loadMessages(false); // Не показываем индикатор загрузки при автообновлении
      }, 3000); // Обновляем каждые 3 секунды
      
      return () => clearInterval(interval);
    }
  }, [orderId, autoRefresh, loadMessages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !receiverId) {
      return;
    }

    const messageContent = newMessage.trim();
    setNewMessage(''); // Очищаем поле сразу

    try {
      setSending(true);
      
      // Создаем временное сообщение для мгновенного отображения
      const tempMessage = {
        id: Date.now(), // Временный ID
        content: messageContent,
        sender_id: user.id,
        receiver_id: receiverId,
        order_id: parseInt(orderId),
        created_at: new Date().toISOString(),
        isTemp: true // Флаг временного сообщения
      };
      
      // Добавляем временное сообщение в интерфейс
      setMessages(prev => [...prev, tempMessage]);

      const messageData = {
        order_id: parseInt(orderId),
        receiver_id: receiverId,
        content: messageContent
      };

      const response = await messagesAPI.create(messageData);
      
      // Заменяем временное сообщение на реальное
      setMessages(prev => prev.map(msg => 
        msg.isTemp && msg.content === messageContent ? response : msg
      ));
      
      // Обновляем lastMessageId
      setLastMessageId(response.id);
      
    } catch (error) {
      toast.error('Ошибка отправки сообщения');
      // Возвращаем сообщение в поле ввода при ошибке
      setNewMessage(messageContent);
    } finally {
      setSending(false);
    }
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера';
    } else {
      return date.toLocaleDateString('ru-RU');
    }
  };

  const isMyMessage = (message) => {
    return message.sender_id === user.id;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Заказ не найден</h2>
          <button
            onClick={() => navigate('/app/orders')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Вернуться к заказам
          </button>
        </div>
      </div>
    );
  }

    return (
    <div className="flex flex-col h-[85vh] bg-gray-50">
      {/* Заголовок */}
      <div className="bg-white border-b px-6 py-4 flex-shrink-0">
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
              <h1 className="text-xl font-semibold text-gray-900">Чат по заказу</h1>
              <p className="text-gray-600 text-sm">{order.title}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              Статус: <span className="font-medium">{order.status}</span>
            </div>
            <div className="text-sm text-gray-500">
              Бюджет: <span className="font-medium text-green-600">{new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB'
              }).format(order.budget)}</span>
            </div>
            {/* Кнопка ручного обновления */}
            <button
              onClick={() => loadMessages(true)}
              className="p-2 rounded-md transition-colors bg-blue-100 text-blue-600 hover:bg-blue-200"
              title="Обновить сообщения"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            {/* Кнопка автообновления */}
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-2 rounded-md transition-colors ${
                autoRefresh 
                  ? 'bg-green-100 text-green-600 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title={autoRefresh ? 'Автообновление включено' : 'Автообновление выключено'}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Сообщения */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 pb-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>Начните общение</p>
          </div>
        ) : (
          messages.map((message, index) => {
            const showDate = index === 0 || 
              formatDate(message.created_at) !== formatDate(messages[index - 1]?.created_at);
            
            return (
              <div key={message.id}>
                {showDate && (
                  <div className="text-center text-gray-500 text-sm mb-4">
                    {formatDate(message.created_at)}
                  </div>
                )}
                <div className={`flex ${isMyMessage(message) ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    isMyMessage(message) 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white border text-gray-800'
                  } ${message.isTemp ? 'opacity-75' : ''}`}>
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      isMyMessage(message) ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {message.isTemp ? 'Отправка...' : formatTime(message.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Форма отправки - внизу с отступом */}
      <div className="bg-white border-t px-6 py-2 flex-shrink-0 shadow-lg">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Введите сообщение..."
            className="flex-1 px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={sending}
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || sending || !receiverId}
            className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {sending ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPage; 