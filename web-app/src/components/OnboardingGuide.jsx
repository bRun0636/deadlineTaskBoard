import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Bot, 
  Plus, 
  Users, 
  FileText, 
  Settings, 
  X,
  ChevronRight,
  Lightbulb
} from 'lucide-react';

const OnboardingGuide = ({ isNewUser = false, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Добро пожаловать в Deadline Task Board!",
      description: "Это платформа для фрилансеров и заказчиков. Давайте быстро познакомимся с основными функциями.",
      icon: Lightbulb,
      color: "text-blue-600"
    },
    {
      title: "Создайте свою первую доску",
      description: "Доски помогают организовать задачи по проектам. Нажмите 'Создать доску' чтобы начать.",
      icon: Plus,
      color: "text-green-600",
      action: "Создать доску",
      actionHandler: () => {
        onClose();
        // Здесь можно добавить навигацию к созданию доски
      }
    },
    {
      title: "Добавьте задачи",
      description: "В каждой доске создавайте задачи с описанием, приоритетом и дедлайнами.",
      icon: FileText,
      color: "text-purple-600"
    },
    {
      title: "Пригласите команду",
      description: "Делитесь досками с коллегами и назначайте исполнителей для задач.",
      icon: Users,
      color: "text-orange-600"
    },
    {
      title: "Используйте Telegram бота",
      description: "Подключите бота для уведомлений и быстрого доступа к задачам.",
      icon: Bot,
      color: "text-teal-600",
      action: "Настроить бота",
      actionHandler: () => {
        onClose();
        // Здесь можно добавить навигацию к настройкам бота
      }
    }
  ];

  const quickActions = [
    {
      title: "Создать доску",
      description: "Организуйте задачи по проектам",
      icon: Plus,
      color: "bg-blue-500",
      link: "/app/boards/create"
    },
    {
      title: "Мои задачи",
      description: "Просмотр назначенных задач",
      icon: FileText,
      color: "bg-green-500",
      link: "/app/tasks"
    },
    {
      title: "Профиль",
      description: "Настройки и личные данные",
      icon: Settings,
      color: "bg-purple-500",
      link: "/app/profile"
    },
    {
      title: "Telegram бот",
      description: "Подключить уведомления",
      icon: Bot,
      color: "bg-teal-500",
      link: "/app/profile"
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  const handleSkip = () => {
    onClose();
  };

  const handleActionClick = () => {
    const currentStepData = steps[currentStep];
    if (currentStepData.actionHandler) {
      currentStepData.actionHandler();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Заголовок */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            🚀 Быстрый старт
          </h2>
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Прогресс */}
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Шаг {currentStep + 1} из {steps.length}
            </span>
            <div className="flex space-x-1">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`h-2 w-2 rounded-full ${
                    index <= currentStep 
                      ? 'bg-blue-500' 
                      : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Текущий шаг */}
        <div className="px-6 py-4">
          <div className="flex items-start space-x-4">
            <div className={`p-3 rounded-lg bg-gray-100 dark:bg-gray-700`}>
              {React.createElement(steps[currentStep].icon, {
                className: `h-6 w-6 ${steps[currentStep].color}`
              })}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                {steps[currentStep].title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {steps[currentStep].description}
              </p>
              {steps[currentStep].action && (
                <button 
                  onClick={handleActionClick}
                  className="btn btn-primary text-sm"
                >
                  {steps[currentStep].action}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Быстрые действия */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
            💡 Быстрые действия
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {quickActions.map((action, index) => (
              <Link
                key={index}
                to={action.link}
                className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className={`p-2 rounded-lg ${action.color} text-white mr-3`}>
                  {React.createElement(action.icon, {
                    className: "h-4 w-4"
                  })}
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {action.title}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {action.description}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Кнопки навигации */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleSkip}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            Пропустить
          </button>
          <button
            onClick={handleNext}
            className="btn btn-primary flex items-center space-x-2"
          >
            <span>
              {currentStep === steps.length - 1 ? 'Завершить' : 'Далее'}
            </span>
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingGuide; 