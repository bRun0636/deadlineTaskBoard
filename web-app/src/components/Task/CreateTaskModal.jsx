import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from 'react-query';
import { X, Calendar, DollarSign, Tag } from 'lucide-react';
import { tasksAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CreateTaskModal = ({
  isOpen,
  onClose,
  boardId,
  columnId,
  assignedToId,
  createdById,
  defaultStatus = 'todo'
}) => {
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: '',
      description: '',
      priority: 'medium',
      tags: '',
      due_date: '',
      budget: '',
    },
  });

  const createTaskMutation = useMutation(
    (data) => {
      // Валидация даты
      let dueDate = null;
      if (data.due_date) {
        try {
          const date = new Date(data.due_date);
          if (isNaN(date.getTime())) {
            throw new Error('Некорректная дата');
          }
          // Проверяем, что год разумный (не меньше 1900 и не больше 2100)
          const year = date.getFullYear();
          if (year < 1900 || year > 2100) {
            throw new Error('Год должен быть между 1900 и 2100');
          }
          dueDate = data.due_date;
        } catch (error) {
          toast.error('Некорректная дата. Пожалуйста, выберите правильную дату.');
          return Promise.reject(error);
        }
      }

      const taskData = {
        title: data.title,
        description: data.description,
        priority: data.priority,
        budget: data.budget ? parseFloat(data.budget) : null,
        due_date: dueDate,
        board_id: parseInt(boardId),
        column_id: columnId ? parseInt(columnId) : null,
        assigned_to_id: assignedToId,
        tags: data.tags ? data.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [],
      };
      
      return tasksAPI.create(taskData);
    },
    {
      onSuccess: (newTask) => {
        // Обновляем кэш для конкретной доски
        queryClient.invalidateQueries(['board', parseInt(boardId)]);
        
        // Также обновляем общие запросы задач
        queryClient.invalidateQueries(['tasks']);
        queryClient.invalidateQueries(['myTasks']);
        queryClient.invalidateQueries(['taskStats']);
        
        // Принудительно обновляем данные доски
        queryClient.refetchQueries(['board', parseInt(boardId)]);
        
        toast.success('Задача успешно создана!');
        reset();
        onClose();
      },
      onError: (error) => {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') {
          toast.error(detail);
        } else if (Array.isArray(detail)) {
          detail.forEach(e => toast.error(e.msg));
        } else if (typeof detail === 'object') {
          toast.error(JSON.stringify(detail));
        } else {
          toast.error('Ошибка при создании задачи');
        }
      },
    }
  );

  const onSubmit = (data) => {
    createTaskMutation.mutate(data);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Создать новую задачу
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Название */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Название задачи *</label>
              <input
                {...register('title', { required: 'Название обязательно' })}
                type="text"
                className="w-full border border-gray-300 rounded p-2"
                placeholder="Введите название задачи"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title.message}</p>
              )}
            </div>

            {/* Описание */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Описание</label>
              <textarea
                {...register('description')}
                rows={3}
                className="w-full border border-gray-300 rounded p-2 resize-none"
                placeholder="Введите описание задачи"
              />
            </div>

            {/* Приоритет */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Приоритет</label>
              <select {...register('priority')} className="w-full border border-gray-300 rounded p-2">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </select>
            </div>

            {/* Дедлайн и Бюджет */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Дедлайн</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    {...register('due_date')}
                    type="datetime-local"
                    min={new Date().toISOString().slice(0, 16)}
                    max="2100-12-31T23:59"
                    className="w-full border border-gray-300 rounded p-2 pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Бюджет</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    {...register('budget')}
                    type="number"
                    step="0.01"
                    className="w-full border border-gray-300 rounded p-2 pl-10"
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>

            {/* Теги */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Теги</label>
              <div className="relative">
                <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('tags')}
                  type="text"
                  className="w-full border border-gray-300 rounded p-2 pl-10"
                  placeholder="tag1, tag2, tag3"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">Разделяйте теги запятыми</p>
            </div>

            {/* Кнопки */}
            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={() => { reset(); onClose(); }}
                className="btn btn-secondary"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={createTaskMutation.isLoading}
                className="btn btn-primary"
              >
                {createTaskMutation.isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  'Создать задачу'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateTaskModal;

