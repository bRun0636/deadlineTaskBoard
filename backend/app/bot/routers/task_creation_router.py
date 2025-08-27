import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from ..keyboards.order_keyboards import (
    get_confirmation_keyboard, get_priority_keyboard
)
from ..keyboards.main_keyboards import get_main_menu_keyboard
from ..services.task_service import TaskService
from ..services.user_service import UserService
from app.models.user import User, UserRole
from app.models.task_status import TaskStatus
from ..states.order_states import CreateTaskStates

router = Router(name="task_creation_router")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "create_task_new")
async def start_create_task(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Начать создание задачи"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await state.set_state(CreateTaskStates.waiting_for_title)
    
    await callback.message.edit_text(
        "📝 <b>Создание новой задачи</b>\n\n"
        "📝 <b>Шаг 1: Название задачи</b>\n\n"
        "Напишите краткое и понятное название вашей задачи.\n\n"
        "💡 <b>Примеры:</b>\n"
        "• Разработать API для мобильного приложения\n"
        "• Создать дизайн лендинга\n"
        "• Написать статью для блога\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CreateTaskStates.waiting_for_title)
async def process_task_title(message: types.Message, state: FSMContext):
    """Обработка названия задачи"""
    if len(message.text) < 5:
        await message.answer(
            "❌ Название слишком короткое! Минимум 5 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(title=message.text)
    await state.set_state(CreateTaskStates.waiting_for_description)
    
    await message.answer(
        "✅ <b>Название сохранено!</b>\n\n"
        "📝 <b>Шаг 2: Описание задачи</b>\n\n"
        "Опишите подробно, что нужно сделать:\n\n"
        "💡 <b>Что указать:</b>\n"
        "• Цель задачи\n"
        "• Технические требования\n"
        "• Желаемый результат\n"
        "• Особые пожелания\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )


@router.message(CreateTaskStates.waiting_for_description)
async def process_task_description(message: types.Message, state: FSMContext):
    """Обработка описания задачи"""
    if len(message.text) < 20:
        await message.answer(
            "❌ Описание слишком короткое! Минимум 20 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(description=message.text)
    await state.set_state(CreateTaskStates.waiting_for_priority)
    
    await message.answer(
        "✅ <b>Описание сохранено!</b>\n\n"
        "🔴 <b>Шаг 3: Выберите приоритет</b>\n\n"
        "Выберите приоритет выполнения задачи:",
        reply_markup=get_priority_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("priority_"))
async def process_task_priority(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора приоритета"""
    priority = callback.data.replace("priority_", "")
    
    # Маппинг приоритетов
    priority_mapping = {
        "high": "Высокий",
        "medium": "Средний", 
        "low": "Низкий"
    }
    
    priority_name = priority_mapping.get(priority, priority)
    await state.update_data(priority=priority)
    
    await state.set_state(CreateTaskStates.waiting_for_deadline)
    
    await callback.message.edit_text(
        f"✅ <b>Приоритет выбран: {priority_name}</b>\n\n"
        "📅 <b>Шаг 4: Сроки выполнения</b>\n\n"
        "Укажите количество дней на выполнение (только число):\n\n"
        "💡 <b>Примеры:</b>\n"
        "• 3 (3 дня)\n"
        "• 7 (неделя)\n"
        "• 14 (2 недели)\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CreateTaskStates.waiting_for_deadline)
async def process_task_deadline(message: types.Message, state: FSMContext):
    """Обработка сроков задачи"""
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
            "❌ Введите корректное число! Например: 7\n"
            "Попробуйте еще раз:"
        )
        return
    
    deadline = datetime.now() + timedelta(days=days)
    await state.update_data(deadline=deadline)
    await state.set_state(CreateTaskStates.waiting_for_budget)
    
    await message.answer(
        "✅ <b>Сроки сохранены!</b>\n\n"
        "💰 <b>Шаг 5: Бюджет задачи</b>\n\n"
        "Укажите бюджет в рублях (только число):\n\n"
        "💡 <b>Примеры:</b>\n"
        "• 5000\n"
        "• 15000\n"
        "• 50000\n\n"
        "🔙 Для отмены нажмите /cancel",
        parse_mode="HTML"
    )


@router.message(CreateTaskStates.waiting_for_budget)
async def process_task_budget(message: types.Message, state: FSMContext):
    """Обработка бюджета задачи"""
    try:
        budget = int(message.text)
        if budget < 100:
            await message.answer(
                "❌ Бюджет слишком маленький! Минимум 100 ₽.\n"
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
            "❌ Введите корректное число! Например: 5000\n"
            "Попробуйте еще раз:"
        )
        return
    
    await state.update_data(budget=budget)
    await state.set_state(CreateTaskStates.waiting_for_confirmation)
    
    # Получаем все данные для подтверждения
    data = await state.get_data()
    
    confirmation_text = (
        "✅ <b>Все данные заполнены!</b>\n\n"
        "📋 <b>Проверьте информацию:</b>\n\n"
        f"📝 <b>Название:</b> {data['title']}\n"
        f"📄 <b>Описание:</b> {data['description'][:100]}...\n"
        f"🔴 <b>Приоритет:</b> {data['priority']}\n"
        f"📅 <b>Срок:</b> {data['deadline'].strftime('%d.%m.%Y')}\n"
        f"💰 <b>Бюджет:</b> {data['budget']:,} ₽\n\n"
        "🔍 <b>Все верно?</b>\n"
        "Нажмите 'Подтвердить' для создания задачи или 'Отменить' для изменения."
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_task_confirmation_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_task_creation")
async def confirm_task_creation(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Подтверждение создания задачи"""
    try:
        data = await state.get_data()
        
        # Создаем задачу через сервис
        task_service = TaskService()
        
        # Создаем задачу в базе данных
        task_data = {
            'title': data['title'],
            'description': data['description'],
            'priority': data['priority'],
            'deadline': data['deadline'],
            'budget': data['budget'],
            'status': TaskStatus.TODO
        }
        
        task = await task_service.create_task(task_data, user.id)
        
        await state.clear()
        
        success_text = (
            "🎉 <b>Задача успешно создана!</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"💰 <b>Бюджет:</b> {task.budget:,} ₽\n"
            f"📅 <b>Срок:</b> {task.deadline.strftime('%d.%m.%Y')}\n\n"
            "✅ <b>Что дальше:</b>\n"
            "• Задача добавлена в ваш список\n"
            "• Вы можете отслеживать прогресс\n"
            "• Назначать исполнителей\n\n"
            "🔍 <b>Просмотреть задачи:</b> /tasks"
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
        logger.error(f"Error creating task: {e}")
        await callback.message.edit_text(
            "❌ <b>Ошибка при создании задачи!</b>\n\n"
            "Произошла техническая ошибка. Попробуйте позже или обратитесь в поддержку.",
            reply_markup=get_main_menu_keyboard(
                user_role=user.role,
                is_admin=user.role == UserRole.ADMIN,
                is_linked=True
            ),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "cancel_task_creation")
async def cancel_task_creation(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Отмена создания задачи"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ <b>Создание задачи отменено</b>\n\n"
        "Вы можете создать задачу позже, нажав '📝 Создать задачу' в главном меню.",
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
        "Вы можете создать задачу позже, нажав '📝 Создать задачу' в главном меню.",
        reply_markup=get_main_menu_keyboard(
            user_role=user.role,
            is_admin=user.role == UserRole.ADMIN,
            is_linked=True
        ),
        parse_mode="HTML"
    )
