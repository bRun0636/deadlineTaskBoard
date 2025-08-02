import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from 'react-query';
import { X, Trash2 } from 'lucide-react';
import { boardsAPI } from '../../services/api';
import toast from 'react-hot-toast';

const BoardSettingsModal = ({ isOpen, onClose, board }) => {
  const queryClient = useQueryClient();
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: board?.title || '',
      description: board?.description || '',
      is_public: board?.is_public || true,
    },
  });

  // Обновляем значения формы при изменении board
  React.useEffect(() => {
    if (board) {
      reset({
        title: board.title || '',
        description: board.description || '',
        is_public: board.is_public || true,
      });
    }
  }, [board, reset]);

  const updateBoardMutation = useMutation(
    (data) => {
      if (!board?.id) {
        throw new Error('ID доски не найден');
      }
      return boardsAPI.update(parseInt(board.id), data);
    },
    {
      onSuccess: (updatedBoard) => {
        // Немедленно обновляем кэш с новыми данными
        queryClient.setQueryData(['board', board.id], updatedBoard);
        queryClient.invalidateQueries('boards');
        toast.success('Настройки доски обновлены!');
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
          toast.error('Ошибка при обновлении доски');
        }
      },
    }
  );

  const deleteBoardMutation = useMutation(
    () => {
      if (!board?.id) {
        throw new Error('ID доски не найден');
      }
      return boardsAPI.delete(parseInt(board.id));
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('boards');
        toast.success('Доска удалена!');
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
          toast.error('Ошибка при удалении доски');
        }
      },
    }
  );

  const onSubmit = (data) => {
    updateBoardMutation.mutate(data);
  };

  const handleDelete = () => {
    if (window.confirm('Вы уверены, что хотите удалить эту доску? Это действие нельзя отменить.')) {
      deleteBoardMutation.mutate();
    }
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
              Настройки доски
            </h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Название доски *
              </label>
              <input
                {...register('title', { required: 'Название обязательно' })}
                type="text"
                className="input"
                placeholder="Введите название доски"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.title.message}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Описание
              </label>
              <textarea
                {...register('description')}
                rows={3}
                className="input resize-none"
                placeholder="Введите описание доски"
              />
            </div>

            <div className="flex items-center">
              <input
                {...register('is_public')}
                type="checkbox"
                id="is_public"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="is_public" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Публичная доска
              </label>
            </div>

            <div className="flex justify-between items-center pt-4">
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleteBoardMutation.isLoading}
                className="btn btn-danger flex items-center gap-2"
              >
                {deleteBoardMutation.isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4" />
                    Удалить доску
                  </>
                )}
              </button>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  className="btn btn-secondary"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={updateBoardMutation.isLoading}
                  className="btn btn-primary"
                >
                  {updateBoardMutation.isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    'Сохранить'
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default BoardSettingsModal; 