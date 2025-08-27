from aiogram.fsm.state import State, StatesGroup


class CreateOrderStates(StatesGroup):
    """Состояния для создания заказа"""
    waiting_for_title = State()  # Ожидание названия заказа
    waiting_for_description = State()  # Ожидание описания
    waiting_for_category = State()  # Ожидание категории
    waiting_for_budget = State()  # Ожидание бюджета
    waiting_for_deadline = State()  # Ожидание сроков
    waiting_for_requirements = State()  # Ожидание требований к исполнителю
    waiting_for_confirmation = State()  # Ожидание подтверждения


class CreateTaskStates(StatesGroup):
    """Состояния для создания задачи"""
    waiting_for_title = State()  # Ожидание названия задачи
    waiting_for_description = State()  # Ожидание описания
    waiting_for_priority = State()  # Ожидание приоритета
    waiting_for_deadline = State()  # Ожидание сроков
    waiting_for_budget = State()  # Ожидание бюджета
    waiting_for_confirmation = State()  # Ожидание подтверждения
