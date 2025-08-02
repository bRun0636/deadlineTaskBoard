/* src/types/dto/OrderDTO.js */

export const OrderStatus = {
  OPEN: "open",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  CANCELLED: "cancelled"
};

export const OrderPriority = {
  LOW: "LOW",
  MEDIUM: "MEDIUM",
  HIGH: "HIGH",
  URGENT: "URGENT"
};

export const OrderDTO = {
  id: "",
  title: "",
  description: "",
  budget: 0,
  deadline: new Date().toISOString(),
  priority: OrderPriority.MEDIUM,
  status: OrderStatus.OPEN,
  tags: "",
  customer_id: null,
  assigned_executor_id: null,
  created_at: new Date().toISOString(),
  updated_at: null,
  completed_at: null,
  proposals: []
};

export function createOrder(overrides = {}) {
  return {
    ...OrderDTO,
    id: crypto.randomUUID(),
    ...overrides,
  };
}

export const OrderStatusLabels = {
  [OrderStatus.OPEN]: "Открыт",
  [OrderStatus.IN_PROGRESS]: "В работе",
  [OrderStatus.COMPLETED]: "Завершен",
  [OrderStatus.CANCELLED]: "Отменен"
};

export const OrderPriorityLabels = {
  [OrderPriority.LOW]: "Низкий",
  [OrderPriority.MEDIUM]: "Средний",
  [OrderPriority.HIGH]: "Высокий",
  [OrderPriority.URGENT]: "Срочный"
};

export const OrderPriorityColors = {
  [OrderPriority.LOW]: "bg-green-100 text-green-800",
  [OrderPriority.MEDIUM]: "bg-blue-100 text-blue-800",
  [OrderPriority.HIGH]: "bg-yellow-100 text-yellow-800",
  [OrderPriority.URGENT]: "bg-red-100 text-red-800"
}; 