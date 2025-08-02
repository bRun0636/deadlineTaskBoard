import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from 'react-query';
import { X } from 'lucide-react';
import { boardsAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CreateBoardModal = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  const createBoardMutation = useMutation(
    (data) => boardsAPI.create(data),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries('boards');
        toast.success('Доска успешно создана!');
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
          toast.error('Ошибка при создании доски');
        }
      },
    }
  );

  const onSubmit = (data) => {
    createBoardMutation.mutate(data);
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
              Создать новую доску
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
                placeholder="Введите описание доски (необязательно)"
              />
            </div>

            <div className="flex items-center">
              <input
                {...register('is_public')}
                type="checkbox"
                id="is_public"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                defaultChecked={true}
              />
              <label htmlFor="is_public" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Публичная доска
              </label>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                className="btn btn-secondary"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={createBoardMutation.isLoading}
                className="btn btn-primary"
              >
                {createBoardMutation.isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  'Создать доску'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateBoardModal; 