import React, { useState, useRef } from 'react';
import { toast } from 'react-toastify';
import { proposalsAPI } from '../../services/api';

const CreateProposalModal = ({ isOpen, onClose, onProposalCreated, orderId }) => {
  const [formData, setFormData] = useState({
    description: '',
    price: '',
    estimated_duration: ''
  });
  const [loading, setLoading] = useState(false);
  const isSubmitting = useRef(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Строгая защита от двойного клика
    if (loading || isSubmitting.current) {
      return;
    }
    
    isSubmitting.current = true;
    setLoading(true);

    try {
      const proposalData = {
        ...formData,
        order_id: orderId,
        price: parseFloat(formData.price),
        estimated_duration: formData.estimated_duration ? parseInt(formData.estimated_duration) : null
      };

      const response = await proposalsAPI.create(proposalData);
      toast.success('Предложение успешно отправлено!');
      
      onProposalCreated(response);
      
      onClose();
      setFormData({
        description: '',
        price: '',
        estimated_duration: ''
      });
    } catch (error) {
      console.error('Ошибка создания предложения:', error);
      const message = error.response?.data?.detail || 'Ошибка создания предложения';
      toast.error(message);
    } finally {
      setLoading(false);
      isSubmitting.current = false;
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Отправить предложение</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Сообщение *
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Опишите ваше предложение, опыт и подход к выполнению заказа"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Цена (₽) *
              </label>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                required
                min="1"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Срок выполнения (дни)
              </label>
              <input
                type="number"
                name="estimated_duration"
                value={formData.estimated_duration}
                onChange={handleChange}
                min="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="7"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Отправка...' : 'Отправить предложение'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProposalModal; 