import React, { useState, useEffect, useRef } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../../hooks/useAuth';
import { messagesAPI } from '../../services/api';

const ChatModal = ({ isOpen, onClose, orderId, orderTitle }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  const [receiverId, setReceiverId] = useState(null);
  const [lastMessageId, setLastMessageId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // Функция для воспроизведения звука уведомления
  const playNotificationSound = () => {
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIG2m98OScTgwOUarm7blmGgU7k9n1unEiBC13yO/eizEIHWq+8+OWT');
      audio.volume = 0.3;
      audio.play();
    } catch (error) {
      console.error('Не удалось воспроизвести звук уведомления');
    }
  };

  useEffect(() => {
    if (isOpen && orderId) {
      loadMessages();
      
      // Устанавливаем интервал для автоматического обновления сообщений
      const interval = setInterval(() => {
        if (isOpen && autoRefresh) { // Обновляем только если чат открыт и автообновление включено
          loadMessages(false); // Не показываем индикатор загрузки при автообновлении
        }
      }, 3000); // Обновляем каждые 3 секунды
      
      // Очищаем интервал при закрытии чата или изменении orderId
      return () => {
        clearInterval(interval);
      };
    }
  }, [isOpen, orderId, autoRefresh]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const response = await messagesAPI.getByOrder(orderId);
      
      // Проверяем, есть ли новые сообщения
      if (response.length > 0) {
        const latestMessage = response[response.length - 1];
        if (lastMessageId !== latestMessage.id) {
          setMessages(response);
          setLastMessageId(latestMessage.id);
          
          // Показываем уведомление о новом сообщении, если чат не в фокусе
          if (!showLoading && latestMessage.sender_id !== user.id) {
            toast.info('Новое сообщение!', {
              position: "top-right",
              autoClose: 3000,
            });
            playNotificationSound(); // Воспроизводим звук уведомления
          }
        }
      } else {
        setMessages(response);
      }
      
      // Определяем ID получателя (противоположная сторона)
      if (response.length > 0) {
        const firstMessage = response[0];
        if (firstMessage.sender_id === user.id) {
          setReceiverId(firstMessage.receiver_id);
        } else {
          setReceiverId(firstMessage.sender_id);
        }
      } else {
        // Если сообщений нет, получаем информацию о заказе для определения получателя
        try {
          const orderResponse = await fetch(`/api/v1/orders/${orderId}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          if (orderResponse.ok) {
            const orderData = await orderResponse.json();
            // Определяем получателя на основе роли пользователя
            if (user.role === 'customer') {
              setReceiverId(orderData.assigned_executor_id);
            } else if (user.role === 'executor') {
              setReceiverId(orderData.creator_id);
            }
          }
        } catch (orderError) {
          console.error('Ошибка получения информации о заказе:', orderError);
        }
      }
    } catch (error) {
      toast.error('Ошибка загрузки сообщений');
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
        order_id: orderId,
        receiver_id: receiverId,
        content: newMessage.trim()
      };

      const response = await messagesAPI.create(messageData);
      setMessages(prev => [...prev, response]);
      setNewMessage('');
      setIsTyping(false);
    } catch (error) {
      toast.error('Ошибка отправки сообщения');
    } finally {
      setSending(false);
    }
  };

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    setIsTyping(e.target.value.length > 0);
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl h-[75vh] flex flex-col">
        {/* Заголовок */}
        <div className="flex justify-between items-center p-4 border-b">
          <div>
            <h2 className="text-xl font-semibold">Чат по заказу</h2>
            <p className="text-gray-600 text-sm">{orderTitle}</p>
          </div>
          <div className="flex items-center space-x-2">
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
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Сообщения */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-1">
          {loading ? (
            <div className="flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : messages.length === 0 ? (
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
                        : 'bg-gray-200 text-gray-800'
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
          <div ref={messagesEndRef} />
          
          {/* Индикатор печати */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm">
                <span className="flex items-center">
                  <span className="mr-2">Печатает</span>
                  <span className="flex space-x-1">
                    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
                    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></span>
                    <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></span>
                  </span>
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Форма отправки */}
        <div className="border-t p-2 shadow-lg">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={handleInputChange}
              placeholder="Введите сообщение..."
              className="flex-1 px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {sending ? 'Отправка...' : 'Отправить'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatModal; 