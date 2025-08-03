import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../../hooks/useAuth';
import { ordersAPI, proposalsAPI } from '../../services/api';
import { OrderStatusLabels, OrderPriorityLabels, OrderPriorityColors } from '../../types/dto/OrderDTO';
import { ProposalStatusLabels, ProposalStatusColors } from '../../types/dto/ProposalDTO';
import CreateProposalModal from '../Proposal/CreateProposalModal';

const OrderDetailsModal = ({ isOpen, onClose, orderId, onProposalCreated }) => {
  const { user } = useAuth();
  const [order, setOrder] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showProposalModal, setShowProposalModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen && orderId) {
      loadOrderDetails();
    }
  }, [isOpen, orderId]);

  const loadOrderDetails = async () => {
    try {
      setLoading(true);
      const orderData = await ordersAPI.getById(orderId);
      setOrder(orderData);
      setProposals(orderData.proposals || []);
    } catch (error) {
      toast.error('Ошибка загрузки деталей заказа');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProposal = async (proposalData) => {
    // Если proposalData уже содержит id, значит предложение уже создано
    if (proposalData.id) {
      loadOrderDetails(); // Перезагружаем данные модала
      
      if (onProposalCreated) {
        onProposalCreated(); // Обновляем родительский компонент
      }
      return;
    }
    
    // Если id нет, создаем предложение (этот код не должен выполняться)
    try {
      await proposalsAPI.create(proposalData);
      loadOrderDetails(); // Перезагружаем данные модала
      
      if (onProposalCreated) {
        onProposalCreated(); // Обновляем родительский компонент
      }
    } catch (error) {
      console.error('Ошибка создания предложения:', error);
      toast.error('Ошибка создания предложения');
    }
  };

  const handleAcceptProposal = async (proposalId) => {
    try {
      await proposalsAPI.accept(proposalId);
      toast.success('Предложение принято!');
      loadOrderDetails();
    } catch (error) {
      toast.error('Ошибка принятия предложения');
    }
  };

  const handleRejectProposal = async (proposalId) => {
    try {
      await proposalsAPI.reject(proposalId);
      toast.success('Предложение отклонено!');
      loadOrderDetails();
    } catch (error) {
      toast.error('Ошибка отклонения предложения');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatBudget = (budget) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB'
    }).format(budget);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold">Детали заказа</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : order ? (
            <div className="space-y-6">
              {/* Основная информация о заказе */}
              <div className="bg-gray-50 rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">{order.title}</h3>
                  <div className="flex space-x-2">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${OrderPriorityColors[order.priority]}`}>
                      {OrderPriorityLabels[order.priority]}
                    </span>
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                      order.status === 'open' ? 'bg-green-100 text-green-800' :
                      order.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      order.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {OrderStatusLabels[order.status]}
                    </span>
                  </div>
                </div>

                <p className="text-gray-700 mb-4">{order.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <span className="text-gray-500 text-sm">Бюджет:</span>
                    <div className="font-semibold text-green-600">{formatBudget(order.budget)}</div>
                  </div>
                  <div>
                    <span className="text-gray-500 text-sm">Дедлайн:</span>
                    <div className="font-semibold">{formatDate(order.deadline)}</div>
                  </div>
                  <div>
                    <span className="text-gray-500 text-sm">Создан:</span>
                    <div className="font-semibold">{formatDate(order.created_at)}</div>
                  </div>
                </div>

                {order.tags && (
                  <div>
                    <span className="text-gray-500 text-sm">Теги:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {order.tags.split(',').map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-200 text-gray-700 text-sm rounded-full"
                        >
                          {tag.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Кнопка чата */}
              {(order.status === 'in_progress' || order.status === 'completed') && (
                <div className="bg-white border rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-semibold">Общение</h3>
                      <p className="text-gray-600 text-sm">Чат с {user.role === 'customer' ? 'исполнителем' : 'заказчиком'}</p>
                    </div>
                    <button
                      onClick={() => navigate(`/chat/${orderId}`)}
                      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center space-x-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      <span>Открыть чат</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Предложения */}
              <div className="bg-white border rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Предложения ({proposals.length})</h3>
                  {user.role === 'executor' && order.status === 'open' && (
                    <button
                      onClick={() => setShowProposalModal(true)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Отправить предложение
                    </button>
                  )}
                </div>

                {proposals.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">
                    Пока нет предложений по этому заказу
                  </p>
                ) : (
                  <div className="space-y-4">
                    {proposals.map((proposal) => (
                      <div key={proposal.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <p className="text-gray-700 mb-2">{proposal.message}</p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">Цена:</span>
                                <div className="font-semibold text-green-600">{formatBudget(proposal.price)}</div>
                              </div>
                              {proposal.estimated_duration && (
                                <div>
                                  <span className="text-gray-500">Срок выполнения:</span>
                                  <div className="font-semibold">{proposal.estimated_duration} дней</div>
                                </div>
                              )}
                              <div>
                                <span className="text-gray-500">Отправлено:</span>
                                <div className="font-semibold">{formatDate(proposal.created_at)}</div>
                              </div>
                            </div>
                          </div>
                          <div className="flex flex-col items-end space-y-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${ProposalStatusColors[proposal.status]}`}>
                              {ProposalStatusLabels[proposal.status]}
                            </span>
                            
                            {/* Действия для заказчика */}
                            {user.role === 'customer' && order.customer_id === user.id && proposal.status === 'pending' && (
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleAcceptProposal(proposal.id)}
                                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                >
                                  Принять
                                </button>
                                <button
                                  onClick={() => handleRejectProposal(proposal.id)}
                                  className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                                >
                                  Отклонить
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Заказ не найден</p>
            </div>
          )}
        </div>
      </div>

      {/* Модальное окно создания предложения */}
      <CreateProposalModal
        isOpen={showProposalModal}
        onClose={() => setShowProposalModal(false)}
        onProposalCreated={handleCreateProposal}
        orderId={orderId}
      />


    </>
  );
};

export default OrderDetailsModal; 