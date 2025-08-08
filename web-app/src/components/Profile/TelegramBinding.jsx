import React, { useState, useEffect } from 'react';
import { Bot, Unlink, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';
import { telegramAPI } from '../../services/api';

const TelegramBinding = ({ user, onUpdate }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [bindingCode, setBindingCode] = useState(null);
  const [telegramId, setTelegramId] = useState('');
  const [telegramUsername, setTelegramUsername] = useState('');
  const [showManualBinding, setShowManualBinding] = useState(false);

  const isTelegramLinked = user?.telegram_id && user?.telegram_username;

  // Функция для проверки статуса привязки
  const checkBindingStatus = async () => {
    try {
      const response = await telegramAPI.getBindingStatus();
      if (response.is_linked && onUpdate) {
        onUpdate(); // Обновляем данные пользователя
      }
    } catch (error) {
      console.error('Ошибка при проверке статуса привязки:', error);
    }
  };

  // Проверяем статус при монтировании и каждые 5 секунд, если пользователь не привязан
  useEffect(() => {
    // Проверяем статус сразу при монтировании
    checkBindingStatus();

    // Устанавливаем интервал проверки, если пользователь не привязан
    if (!isTelegramLinked) {
      const interval = setInterval(checkBindingStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [isTelegramLinked, checkBindingStatus]);

  const generateBindingCode = async () => {
    setIsLoading(true);
    try {
      const response = await telegramAPI.generateBindingCode();
      setBindingCode(response.code);
      toast.success('Код для привязки сгенерирован!');
    } catch (error) {
      toast.error('Ошибка при генерации кода');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyCode = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      toast.success('Код скопирован в буфер обмена!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Не удалось скопировать код');
    }
  };

  const handleUnlinkTelegram = async () => {
    if (!window.confirm('Вы уверены, что хотите отвязать Telegram аккаунт?')) {
      return;
    }

    setIsLoading(true);
    try {
      await telegramAPI.unlinkTelegram();
      toast.success('Telegram аккаунт отвязан!');
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      toast.error('Ошибка при отвязке аккаунта');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBindByTelegramId = async () => {
    if (!telegramId.trim() || !telegramUsername.trim()) {
      toast.error('Пожалуйста, заполните все поля');
      return;
    }

    setIsLoading(true);
    try {
      await telegramAPI.bindByTelegramId(parseInt(telegramId), telegramUsername);
      toast.success('Telegram аккаунт успешно привязан!');
      setTelegramId('');
      setTelegramUsername('');
      setShowManualBinding(false);
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      toast.error('Ошибка при привязке аккаунта');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Привязка Telegram
        </h2>
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-blue-600" />
          {isTelegramLinked ? (
            <span className="text-sm text-green-600 font-medium">Подключен</span>
          ) : (
            <span className="text-sm text-gray-500">Не подключен</span>
          )}
        </div>
      </div>

      {isTelegramLinked ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center">
                <Bot className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">
                  @{user.telegram_username}
                </p>
                <p className="text-sm text-gray-500">
                  ID: {user.telegram_id}
                </p>
              </div>
            </div>
            <button
              onClick={handleUnlinkTelegram}
              disabled={isLoading}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
            >
              <Unlink className="h-4 w-4" />
              <span>Отвязать</span>
            </button>
          </div>
          
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p>✅ Ваш Telegram аккаунт успешно привязан к профилю.</p>
            <p>Вы будете получать уведомления о новых заказах, сообщениях и обновлениях задач.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
              Как привязать Telegram?
            </h3>
            <div className="flex space-x-4 mb-4">
              <button
                onClick={() => setShowManualBinding(false)}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  !showManualBinding 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Через бота
              </button>
              <button
                onClick={() => setShowManualBinding(true)}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  showManualBinding 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                По ID
              </button>
            </div>
            
            {!showManualBinding ? (
              <ol className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                <li>1. Найдите нашего бота в Telegram: <span className="font-mono text-blue-600">@myTestWorkqwe_Bot</span></li>
                <li>2. Отправьте боту команду: <span className="font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">/start</span></li>
                <li>3. Скопируйте код ниже и отправьте его боту</li>
              </ol>
            ) : (
              <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                <p>Введите ваш Telegram ID и username для привязки:</p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Telegram ID:
                    </label>
                    <input
                      type="number"
                      value={telegramId}
                      onChange={(e) => setTelegramId(e.target.value)}
                      placeholder="your_telegram_id"
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Username (без @):
                    </label>
                    <input
                      type="text"
                      value={telegramUsername}
                      onChange={(e) => setTelegramUsername(e.target.value)}
                      placeholder="username"
                      className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    />
                  </div>
                  <button
                    onClick={handleBindByTelegramId}
                    disabled={isLoading}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Привязка...' : 'Привязать аккаунт'}
                  </button>
                </div>
              </div>
            )}
          </div>

          {!showManualBinding && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Код для привязки:
                </label>
                <button
                  onClick={generateBindingCode}
                  disabled={isLoading}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  {isLoading ? 'Генерация...' : 'Сгенерировать код'}
                </button>
              </div>
              
              {bindingCode ? (
                <div className="flex items-center space-x-2">
                  <div className="flex-1 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border">
                    <code className="text-sm font-mono text-gray-900 dark:text-gray-100">
                      {bindingCode}
                    </code>
                  </div>
                  <button
                    onClick={() => handleCopyCode(bindingCode)}
                    className="p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title="Скопировать код"
                  >
                    {copied ? (
                      <Check className="h-5 w-5 text-green-600" />
                    ) : (
                      <Copy className="h-5 w-5" />
                    )}
                  </button>
                </div>
              ) : (
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border text-center text-gray-500">
                  Нажмите "Сгенерировать код" для получения кода привязки
                </div>
              )}
            </div>
          )}

          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p>⚠️ Код действителен в течение 10 минут. После отправки кода боту, ваш аккаунт будет автоматически привязан.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TelegramBinding; 