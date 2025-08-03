import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    if (orderId) {
      loadOrderAndMessages();
    }
  }, [orderId]);

  const loadOrderAndMessages = async () => {
    try {
      setLoading(true);
      
      // Загружаем информацию о заказе
      const orderData = await ordersAPI.getById(orderId);
      setOrder(orderData);
      
      // Определяем получателя на основе роли пользователя
      if (user.role === 'customer') {
        setReceiverId(orderData.assigned_executor_id);
      } else if (user.role === 'executor') {
        setReceiverId(orderData.customer_id);
      }
      
      // Загружаем сообщения
      const messagesData = await messagesAPI.getByOrder(orderId);
      setMessages(messagesData);
      
    } catch (error) {
      toast.error('Ошибка загрузки данных');
      navigate('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !receiverId) {
      return;
    }

    try {
      setSending(true);
      const messageData = {
        order_id: parseInt(orderId),
        receiver_id: receiverId,
        content: newMessage.trim()
      };

      const response = await messagesAPI.create(messageData);
      setMessages(prev => [...prev, response]);
      setNewMessage('');
    } catch (error) {
      toast.error('Ошибка отправки сообщения');
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
            onClick={() => navigate('/orders')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Вернуться к заказам
          </button>
        </div>
      </div>
    );
  }

    return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-white border-b px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/orders')}
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
          </div>
        </div>
      </div>

      {/* Сообщения */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 pb-16">
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
                  }`}>
                    <p className="text-sm">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      isMyMessage(message) ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {formatTime(message.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Форма отправки - фиксированная внизу */}
      <div className="bg-white border-t px-6 py-8 flex-shrink-0">
        <form onSubmit={handleSendMessage} className="flex space-x-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Введите сообщение..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={sending}
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || sending || !receiverId}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {sending ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPage; 