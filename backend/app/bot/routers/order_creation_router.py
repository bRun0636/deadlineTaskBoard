import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from ..keyboards.order_keyboards import (
    get_confirmation_keyboard, get_category_keyboard, get_priority_keyboard
)
from ..keyboards.main_keyboards import get_main_menu_keyboard
from ..services.order_service import OrderService
from ..services.user_service import UserService
from app.models.user import User, UserRole
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate
from ..states.order_states import CreateOrderStates

router = Router(name="order_creation_router")
logger = logging.getLogger(__name__)


# Состояния уже определены в states/order_states.py


@router.callback_query(F.data == "create_order")
async def start_create_order(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Начать создание заказа"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Проверяем роль пользователя
    if user.role not in [UserRole.CUSTOMER, UserRole.ADMIN]:
        await callback.answer("❌ Только заказчики могут создавать заказы!", show_alert=True)
        return
    
    await state.set_state(CreateOrderStates.waiting_for_title)
    
    await callback.message.edit_text(
        "➕ <b>Создание нового заказа</b>\n\n"
        "📝 <b>Шаг 1: Название проекта</b>\n\n"
        "Напишите краткое и понятное название вашего проекта.\n\n"
        "💡 <b>Примеры:</b>\n"
        "• Создание лендинга для интернет-магазина\n"
        "• Разработка мобильного приложения\n"
        "• Дизайн корпоративного сайта\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CreateOrderStates.waiting_for_title)
async def process_order_title(message: types.Message, state: FSMContext):
    """Обработка названия заказа"""
    if len(message.text) < 5:
        await message.answer(
            "❌ Название слишком короткое! Минимум 5 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(title=message.text)
    await state.set_state(CreateOrderStates.waiting_for_description)
    
    await message.answer(
        "✅ <b>Название сохранено!</b>\n\n"
        "📝 <b>Шаг 2: Описание задачи</b>\n\n"
        "Опишите подробно, что нужно сделать:\n\n"
        "💡 <b>Что указать:</b>\n"
        "• Цель проекта\n"
        "• Технические требования\n"
        "• Желаемый результат\n"
        "• Особые пожелания\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )


@router.message(CreateOrderStates.waiting_for_description)
async def process_order_description(message: types.Message, state: FSMContext):
    """Обработка описания заказа"""
    if len(message.text) < 20:
        await message.answer(
            "❌ Описание слишком короткое! Минимум 20 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(description=message.text)
    await state.set_state(CreateOrderStates.waiting_for_category)
    
    await message.answer(
        "✅ <b>Описание сохранено!</b>\n\n"
        "📂 <b>Шаг 3: Выберите категорию</b>\n\n"
        "Выберите наиболее подходящую категорию для вашего проекта:",
        reply_markup=get_category_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("category_"))
async def process_order_category(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора категории"""
    category = callback.data.replace("category_", "")
    
    # Маппинг категорий
    category_mapping = {
        "development": "Разработка",
        "design": "Дизайн", 
        "copywriting": "Копирайтинг",
        "smm": "SMM",
        "seo": "SEO",
        "analytics": "Аналитика"
    }
    
    category_name = category_mapping.get(category, category)
    await state.update_data(category=category)
    
    await state.set_state(CreateOrderStates.waiting_for_budget)
    
    await callback.message.edit_text(
        f"✅ <b>Категория выбрана: {category_name}</b>\n\n"
        "💰 <b>Шаг 4: Бюджет проекта</b>\n\n"
        "Укажите бюджет в рублях (только число):\n\n"
        "💡 <b>Примеры:</b>\n"
        "• 50000\n"
        "• 100000\n"
        "• 250000\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CreateOrderStates.waiting_for_budget)
async def process_order_budget(message: types.Message, state: FSMContext):
    """Обработка бюджета заказа"""
    try:
        budget = int(message.text)
        if budget < 1000:
            await message.answer(
                "❌ Бюджет слишком маленький! Минимум 1000 ₽.\n"
                "Попробуйте еще раз:"
            )
            return
        if budget > 1000000:
            await message.answer(
                "❌ Бюджет слишком большой! Максимум 1,000,000 ₽.\n"
                "Попробуйте еще раз:"
            )
            return
    except ValueError:
        await message.answer(
            "❌ Введите корректное число! Например: 50000\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(budget=budget)
    await state.set_state(CreateOrderStates.waiting_for_deadline)
    
    await message.answer(
        "✅ <b>Бюджет сохранен!</b>\n\n"
        "📅 <b>Шаг 5: Сроки выполнения</b>\n\n"
        "Укажите количество дней на выполнение (только число):\n\n"
        "💡 <b>Примеры:</b>\n"
        "• 7 (неделя)\n"
        "• 14 (2 недели)\n"
        "• 30 (месяц)\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )


@router.message(CreateOrderStates.waiting_for_deadline)
async def process_order_deadline(message: types.Message, state: FSMContext):
    """Обработка сроков заказа"""
    try:
        days = int(message.text)
        if days < 1:
            await message.answer(
                "❌ Срок должен быть больше 0 дней!\n"
                "Попробуйте еще раз:"
            )
            return
        if days > 365:
            await message.answer(
                "❌ Срок слишком большой! Максимум 365 дней.\n"
                "Попробуйте еще раз:"
            )
            return
    except ValueError:
        await message.answer(
            "❌ Введите корректное число! Например: 14\n"
            "Попробуйте еще раз:"
        )
        return
    
    deadline = datetime.now() + timedelta(days=days)
    await state.update_data(deadline=deadline)
    await state.set_state(CreateOrderStates.waiting_for_requirements)
    
    await message.answer(
        "✅ <b>Сроки сохранены!</b>\n\n"
        "👨‍💻 <b>Шаг 6: Требования к исполнителю</b>\n\n"
        "Опишите, какими навыками должен обладать исполнитель:\n\n"
        "💡 <b>Что указать:</b>\n"
        "• Опыт работы\n"
        "• Технологии\n"
        "• Портфолио\n"
        "• Дополнительные требования\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )


@router.message(CreateOrderStates.waiting_for_requirements)
async def process_order_requirements(message: types.Message, state: FSMContext):
    """Обработка требований к исполнителю"""
    if len(message.text) < 10:
        await message.answer(
            "❌ Описание требований слишком короткое! Минимум 10 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(requirements=message.text)
    await state.set_state(CreateOrderStates.waiting_for_confirmation)
    
    # Получаем все данные для подтверждения
    data = await state.get_data()
    
    confirmation_text = (
        "✅ <b>Все данные заполнены!</b>\n\n"
        "📋 <b>Проверьте информацию:</b>\n\n"
        f"📝 <b>Название:</b> {data['title']}\n"
        f"📄 <b>Описание:</b> {data['description'][:100]}...\n"
        f"📂 <b>Категория:</b> {data['category']}\n"
        f"💰 <b>Бюджет:</b> {data['budget']:,} ₽\n"
        f"📅 <b>Срок:</b> {data['deadline'].strftime('%d.%m.%Y')}\n"
        f"👨‍💻 <b>Требования:</b> {data['requirements'][:100]}...\n\n"
        "🔍 <b>Все верно?</b>\n"
        "Нажмите 'Подтвердить' для создания заказа или 'Отменить' для изменения."
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_order_creation")
async def confirm_order_creation(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Подтверждение создания заказа"""
    try:
        data = await state.get_data()
        
        # Создаем заказ через сервис
        order_service = OrderService()
        
        # Создаем заказ в базе данных
        order_data = {
            'title': data['title'],
            'description': data['description'],
            'category': data['category'],
            'budget': data['budget'],
            'deadline': data['deadline'],
            'requirements': data['requirements'],
            'status': OrderStatus.OPEN
        }
        
        order = await order_service.create_order(order_data, user.id)
        
        await state.clear()
        
        success_text = (
            "🎉 <b>Заказ успешно создан!</b>\n\n"
            f"📝 <b>Название:</b> {order.title}\n"
            f"💰 <b>Бюджет:</b> {order.budget:,} ₽\n"
            f"📅 <b>Срок:</b> {order.deadline.strftime('%d.%m.%Y')}\n\n"
            "✅ <b>Что дальше:</b>\n"
            "• Исполнители увидят ваш заказ\n"
            "• Они будут предлагать свои услуги\n"
            "• Вы сможете выбрать лучшего исполнителя\n\n"
            "🔍 <b>Просмотреть заказ:</b> /orders"
        )
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(
                user_role=user.role,
                is_admin=user.role == UserRole.ADMIN,
                is_linked=True
            ),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await callback.message.edit_text(
            "❌ <b>Ошибка при создании заказа!</b>\n\n"
            "Произошла техническая ошибка. Попробуйте позже или обратитесь в поддержку.",
            reply_markup=get_main_menu_keyboard(
                user_role=user.role,
                is_admin=user.role == UserRole.ADMIN,
                is_linked=True
            ),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "cancel_order_creation")
async def cancel_order_creation(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Отмена создания заказа"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ <b>Создание заказа отменено</b>\n\n"
        "Вы можете создать заказ позже, нажав '➕ Создать заказ' в главном меню.",
        reply_markup=get_main_menu_keyboard(
            user_role=user.role,
            is_admin=user.role == UserRole.ADMIN,
            is_linked=True
        ),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cancel_creation_command(message: types.Message, state: FSMContext, user: User):
    """Команда отмены создания"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нечего отменять!")
        return
    
    await state.clear()
    
    await message.answer(
        "❌ <b>Создание отменено</b>\n\n"
        "Вы можете создать заказ позже, нажав '➕ Создать заказ' в главном меню.",
        reply_markup=get_main_menu_keyboard(
            user_role=user.role,
            is_admin=user.role == UserRole.ADMIN,
            is_linked=True
        ),
        parse_mode="HTML"
    )
