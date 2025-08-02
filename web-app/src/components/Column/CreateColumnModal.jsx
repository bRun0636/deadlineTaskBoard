import React from 'react';
import { useForm } from 'react-hook-form';

const CreateColumnModal = ({ isOpen, onClose, onCreate, boardId }) => {
  const {
    register,
    handleSubmit,
    reset,
  } = useForm();

  const onSubmit = (data) => {
    // Передача данных в родительский компонент
    onCreate({
      ...data,
      board_id: boardId,
    });
    reset();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-lg w-full shadow-lg relative">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Создать новую колонку</h2>
          <button
            onClick={() => {
              reset();
              onClose();
            }}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            &times;
          </button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Название */}
          <div>
            <label className="block mb-1 font-medium text-gray-700 dark:text-gray-300">Название</label>
            <input
              {...register('name', { required: 'Название обязательно' })}
              type="text"
              className="w-full border border-gray-300 rounded p-2"
              placeholder="Введите название колонки"
            />
          </div>

          {/* Кнопки */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                reset();
                onClose();
              }}
              className="btn btn-secondary"
            >
              Отмена
            </button>
            <button
              type="submit"
              className="btn btn-primary"
            >
              Создать
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateColumnModal;