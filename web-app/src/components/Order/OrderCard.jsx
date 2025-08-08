import React from 'react';
import { OrderStatusLabels, OrderPriorityLabels, OrderPriorityColors } from '../../types/dto/OrderDTO';

const OrderCard = ({ order, onViewDetails, onEdit, onDelete, onComplete, onCancel, onRestore, onTakeOrder, userRole, currentUserId }) => {
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

  const getProposalStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'На рассмотрении';
      case 'accepted':
        return 'Принято';
      case 'rejected':
        return 'Отклонено';
      case 'withdrawn':
        return 'Отозвано';
      default:
        return 'Неизвестно';
    }
  };

  const getProposalStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-blue-50 text-blue-700 border border-blue-200';
      case 'accepted':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
      case 'rejected':
        return 'bg-rose-50 text-rose-700 border border-rose-200';
      case 'withdrawn':
        return 'bg-slate-50 text-slate-600 border border-slate-200';
      default:
        return 'bg-slate-50 text-slate-600 border border-slate-200';
    }
  };

            const isCustomer = userRole === 'customer';
            const isAdmin = userRole === 'admin';
            const isExecutor = userRole === 'executor';
            
            // Проверяем, является ли текущий пользователь создателем заказа
            const isOrderCreator = currentUserId && order.creator_id && Number(currentUserId) === Number(order.creator_id);
            
            // Проверяем, есть ли уже предложение от текущего пользователя
            const hasUserProposal = order.proposals && order.proposals.some(proposal => 
              proposal.user_id === Number(currentUserId)
            );
            
            // Правильная логика отображения кнопок
            const canManageOrder = (isCustomer && isOrderCreator) || isAdmin;
            const canTakeOrder = (isExecutor || (isAdmin && !isOrderCreator)) && order.status === 'open' && !hasUserProposal;
            
            // Отладочная информация удалена для продакшена

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow h-full flex flex-col">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
          {order.title}
        </h3>
        <div className="flex space-x-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${OrderPriorityColors[order.priority]}`}>
            {OrderPriorityLabels[order.priority]}
          </span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
            order.status === 'open' ? 'bg-green-100 text-green-800' :
            order.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
            order.status === 'completed' ? 'bg-gray-100 text-gray-800' :
            'bg-red-100 text-red-800'
          }`}>
            {OrderStatusLabels[order.status]}
          </span>
        </div>
      </div>

      <div className="flex-grow">
        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {order.description}
        </p>

        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500">Бюджет:</span>
          <div className="font-semibold text-green-600">{formatBudget(order.budget)}</div>
        </div>
        <div>
          <span className="text-gray-500">Дедлайн:</span>
          <div className="font-semibold">{formatDate(order.deadline)}</div>
        </div>
      </div>

      {order.tags && (
        <div className="mb-4">
          <span className="text-gray-500 text-sm">Теги:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {order.tags.split(',').map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {tag.trim()}
              </span>
            ))}
          </div>
        </div>
      )}

        {order.proposals && order.proposals.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2">
              <span className="text-gray-500 text-sm">
                Предложений: {order.proposals.length}
              </span>
              {/* Показываем статус предложения текущего пользователя */}
              {order.proposals.some(proposal => proposal.user_id === Number(currentUserId)) && (
                (() => {
                  const userProposal = order.proposals.find(proposal => proposal.user_id === Number(currentUserId));
                  // Показываем статус только если он не "pending" или если это единственное предложение
                  if (userProposal.status !== 'pending' || order.proposals.length === 1) {
                    return (
                      <span className={`text-xs px-2 py-1 rounded-full flex items-center gap-1 ${getProposalStatusColor(userProposal.status)}`}>
                        <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70"></span>
                        {getProposalStatusText(userProposal.status)}
                      </span>
                    );
                  }
                  return null;
                })()
              )}
            </div>
          </div>
        )}
      </div>

      <div className="space-y-3">
        <div className="text-xs text-gray-500">
          Создан: {formatDate(order.created_at)}
        </div>
        
        <div className="flex flex-wrap gap-1 sm:gap-2">
          <button
            onClick={() => onViewDetails(order)}
            className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Подробнее
          </button>
          
          {canTakeOrder && (
            <button
              onClick={() => onTakeOrder(order)}
              className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
            >
              Принять заказ
            </button>
          )}
          
          {canManageOrder && (
            <>
              {order.status === 'open' && (
                <button
                  onClick={() => onEdit(order)}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                >
                  Редактировать
                </button>
              )}
              
              {order.status === 'in_progress' && (
                <button
                  onClick={() => onComplete(order.id)}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  Завершить
                </button>
              )}
              
              {(order.status === 'open' || order.status === 'in_progress') && (
                <button
                  onClick={() => onCancel(order.id)}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Отменить
                </button>
              )}
              
              {order.status === 'open' && (
                <button
                  onClick={() => onDelete(order.id)}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                >
                  Удалить
                </button>
              )}
              
              {order.status === 'cancelled' && (
                <>
                  <button
                    onClick={() => onRestore(order.id)}
                    className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                  >
                    Восстановить
                  </button>
                  <button
                    onClick={() => onDelete(order.id)}
                    className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                  >
                    Удалить
                  </button>
                </>
              )}
              
              {order.status === 'completed' && (
                <button
                  onClick={() => onDelete(order.id)}
                  className="px-2 sm:px-3 py-1 text-xs sm:text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Удалить
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderCard; 