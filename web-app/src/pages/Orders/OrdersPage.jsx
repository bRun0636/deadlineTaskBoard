import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../../hooks/useAuth';
import { ordersAPI } from '../../services/api';
import OrderCard from '../../components/Order/OrderCard';
import CreateOrderModal from '../../components/Order/CreateOrderModal';
import EditOrderModal from '../../components/Order/EditOrderModal';
import OrderDetailsModal from '../../components/Order/OrderDetailsModal';

const OrdersPage = () => {
  const { user } = useAuth();
  
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadOrders();
  }, [filter, user?.role]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadOrders = async () => {
    try {
      setLoading(true);
      let response;
      
      if (user?.role === 'admin') {
        // Администраторы видят все заказы
        response = await ordersAPI.getAll();
      } else if (user?.role === 'executor') {
        // Для исполнителей показываем все доступные заказы
        if (filter === 'open') {
          response = await ordersAPI.getOpen();
        } else {
          response = await ordersAPI.getAll();
        }
      } else {
        // Для заказчиков показываем их собственные заказы
        response = await ordersAPI.getMy();
      }
      
      setOrders(response);
    } catch (error) {
      toast.error('Ошибка загрузки заказов');
    } finally {
      setLoading(false);
    }
  };

  const handleOrderCreated = (newOrder) => {
    setOrders(prev => [newOrder, ...prev]);
  };

  const handleOrderDeleted = (orderId) => {
    setOrders(prev => prev.filter(order => order.id !== orderId));
  };

  const handleOrderUpdated = (updatedOrder) => {
    setOrders(prev => prev.map(order => 
      order.id === updatedOrder.id ? updatedOrder : order
    ));
  };

  const handleComplete = async (orderId) => {
    try {
      const updatedOrder = await ordersAPI.complete(orderId);
      handleOrderUpdated(updatedOrder);
      toast.success('Заказ успешно завершен!');
    } catch (error) {
      toast.error('Ошибка завершения заказа');
    }
  };

  const handleCancel = async (orderId) => {
    try {
      const updatedOrder = await ordersAPI.cancel(orderId);
      handleOrderUpdated(updatedOrder);
      toast.success('Заказ успешно отменен!');
    } catch (error) {
      toast.error(`Ошибка отмены заказа: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRestore = async (orderId) => {
    try {
      const updatedOrder = await ordersAPI.restore(orderId);
      handleOrderUpdated(updatedOrder);
      toast.success('Заказ успешно восстановлен!');
    } catch (error) {
      toast.error('Ошибка восстановления заказа');
    }
  };

  const handleDelete = async (orderId) => {
    if (window.confirm('Вы уверены, что хотите удалить этот заказ?')) {
      try {
        await ordersAPI.delete(orderId);
        handleOrderDeleted(orderId);
        toast.success('Заказ успешно удален!');
      } catch (error) {
        toast.error('Ошибка удаления заказа');
      }
    }
  };

  const handleViewDetails = (order) => {
    setSelectedOrderId(order.id);
    setShowDetailsModal(true);
  };

  const handleEdit = (order) => {
    setSelectedOrder(order);
    setShowEditModal(true);
  };

  const handleTakeOrder = (order) => {
    setSelectedOrder(order);
    setShowDetailsModal(true);
    setSelectedOrderId(order.id);
  };

  const filteredOrders = orders.filter(order => {
    if (filter === 'all') return true;
    return order.status === filter;
  });

  const isCustomer = user?.role === 'customer';
  const isAdmin = user?.role === 'admin';
  const canCreateOrders = isCustomer || isAdmin;
  const shouldShowCreateButton = canCreateOrders && (filter === 'all' || filter === 'open');

  // Если пользователь не загружен, показываем загрузку
  if (!user) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          {isCustomer ? 'Мои заказы' : 'Доступные заказы'}
        </h1>
        
        {shouldShowCreateButton && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Создать заказ
          </button>
        )}
      </div>

      {/* Фильтры */}
      <div className="mb-6">
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              filter === 'all' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Все
          </button>
          <button
            onClick={() => setFilter('open')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              filter === 'open' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Открытые
          </button>
          <button
            onClick={() => setFilter('in_progress')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              filter === 'in_progress' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            В работе
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              filter === 'completed' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Завершенные
          </button>
          <button
            onClick={() => setFilter('cancelled')}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              filter === 'cancelled' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Отмененные
          </button>
        </div>
      </div>

      {/* Список заказов */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredOrders.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-4">
            {filter === 'all' && (
              isCustomer 
                ? 'У вас пока нет заказов' 
                : isAdmin
                ? 'В системе пока нет заказов'
                : 'Нет доступных заказов'
            )}
            {filter === 'open' && (
              isCustomer 
                ? 'У вас нет открытых заказов' 
                : isAdmin
                ? 'В системе нет открытых заказов'
                : 'Нет доступных открытых заказов'
            )}
            {filter === 'in_progress' && (
              isCustomer 
                ? 'У вас нет заказов в работе' 
                : isAdmin
                ? 'В системе нет заказов в работе'
                : 'Нет заказов в работе'
            )}
            {filter === 'completed' && (
              isCustomer 
                ? 'У вас нет завершенных заказов' 
                : isAdmin
                ? 'В системе нет завершенных заказов'
                : 'Нет завершенных заказов'
            )}
            {filter === 'cancelled' && (
              isCustomer 
                ? 'У вас нет отмененных заказов' 
                : isAdmin
                ? 'В системе нет отмененных заказов'
                : 'Нет отмененных заказов'
            )}
          </div>
          {shouldShowCreateButton && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              {isCustomer ? 'Создать первый заказ' : 'Создать заказ'}
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-stretch">
          {filteredOrders.map(order => (
            <OrderCard
              key={order.id}
              order={order}
              userRole={user?.role}
              currentUserId={user?.id}
              onViewDetails={handleViewDetails}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onComplete={handleComplete}
              onCancel={handleCancel}
              onRestore={handleRestore}
              onTakeOrder={handleTakeOrder}
            />
          ))}
        </div>
      )}

                    {/* Модальное окно создания заказа */}
              <CreateOrderModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onOrderCreated={handleOrderCreated}
              />

              {/* Модальное окно редактирования заказа */}
              <EditOrderModal
                isOpen={showEditModal}
                onClose={() => {
                  setShowEditModal(false);
                  setSelectedOrder(null);
                }}
                order={selectedOrder}
                onOrderUpdated={handleOrderUpdated}
              />

              {/* Модальное окно деталей заказа */}
              <OrderDetailsModal
                isOpen={showDetailsModal}
                onClose={() => setShowDetailsModal(false)}
                orderId={selectedOrderId}
                onProposalCreated={loadOrders}
              />
    </div>
  );
};

export default OrdersPage; 