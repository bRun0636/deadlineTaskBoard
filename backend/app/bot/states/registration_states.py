from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    """Состояния для регистрации пользователя"""
    phone = State()
    role = State()
    country = State()
    juridical_type = State()
    payment_types = State()
    prof_level = State()
    skills = State()
    bio = State()
    notifications = State()

class TaskCreation(StatesGroup):
    """Состояния для создания задачи"""
    title = State()
    description = State()
    budget = State()
    deadline = State()
    priority = State()
    tags = State()
    confirmation = State()

class OrderCreation(StatesGroup):
    """Состояния для создания заказа"""
    title = State()
    description = State()
    budget = State()
    deadline = State()
    priority = State()
    tags = State()

class ProposalCreation(StatesGroup):
    """Состояния для создания предложения"""
    price = State()
    description = State()
    duration = State()

class ProfileEdit(StatesGroup):
    """Состояния для редактирования профиля"""
    field = State()
    value = State() 