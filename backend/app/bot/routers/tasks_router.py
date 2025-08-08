import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from ..states.registration_states import TaskCreation
from ..keyboards.main_keyboards import (
    get_main_menu_keyboard, get_task_actions_keyboard,
    get_priority_keyboard, get_confirmation_keyboard
)
from ..keyboards.task_keyboards import get_tasks_menu_keyboard
from ..services.user_service import UserService
from ..services.task_service import TaskService
from app.models.task_status import TaskStatus
from app.models.task_type import TaskType
from app.models.user import User

router = Router(name="tasks_router")
logger = logging.getLogger(__name__)

@router.message(Command("tasks"))
async def show_tasks_menu(message: types.Message, user: User):
    """Показать меню задач"""
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы должны быть зарегистрированы для работы с задачами.\n"
            "Используйте /register для регистрации."
        )
        return
    
    await message.answer(
        "📋 <b>Управление задачами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_task_actions_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "my_tasks")
async def show_my_tasks(callback: types.CallbackQuery, user: User):
    """Показать мои задачи"""
    # Проверяем, привязан ли аккаунт к сайту
    # is_linked = True если пользователь зарегистрирован на сайте (имеет email) и привязан к Telegram
    is_linked = user and user.email and user.telegram_id == callback.from_user.id
    
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_service = TaskService()
        tasks = await task_service.get_user_tasks(user.id)
        
        if not tasks:
            await callback.message.edit_text(
                "📋 <b>Мои задачи</b>\n\n"
                "У вас пока нет задач.\n"
                "Создайте новую задачу!",
                reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
                parse_mode="HTML"
            )
            return
        
        # Формируем список задач
        tasks_text = "📋 <b>Мои задачи:</b>\n\n"
        for i, task in enumerate(tasks[:10], 1):  # Показываем первые 10
            status_emoji = {
                TaskStatus.TODO: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.DONE: "✅",
                TaskStatus.CANCELLED: "❌"
            }.get(task.status, "📝")
            
            tasks_text += (
                f"{i}. {status_emoji} <b>{task.title}</b>\n"
                f"   Статус: {task.status.value}\n"
                f"   Приоритет: {task.priority}\n"
                f"   Бюджет: {task.budget or 'Не указан'} ₽\n\n"
            )
        
        if len(tasks) > 10:
            tasks_text += f"... и еще {len(tasks) - 10} задач"
        
        await callback.message.edit_text(
            tasks_text,
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error showing tasks for user {user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке задач.",
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked)
        )

@router.callback_query(F.data == "create_task")
async def start_create_task(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Начать создание задачи"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await state.set_state(TaskCreation.title)
    await callback.message.edit_text(
        "📝 <b>Создание новой задачи</b>\n\n"
        "📋 <b>Шаг 1: Название задачи</b>\n\n"
        "💡 <b>Как написать хорошее название:</b>\n"
        "• Кратко и понятно\n"
        "• Укажите тип работы\n"
        "• Добавьте ключевые слова\n\n"
        "📝 <b>Примеры хороших названий:</b>\n"
        "• Создать лендинг для интернет-магазина\n"
        "• Разработать мобильное приложение\n"
        "• Написать статьи для блога\n"
        "• Сделать дизайн логотипа\n\n"
        "❌ <b>Плохие примеры:</b>\n"
        "• Нужна помощь\n"
        "• Сделать сайт\n"
        "• Работа\n\n"
        "🎯 <b>Введите название вашей задачи:</b>",
        parse_mode="HTML"
    )

@router.message(TaskCreation.title)
async def get_task_title(message: types.Message, state: FSMContext):
    """Получить название задачи"""
    title = message.text.strip()
    
    if len(title) < 3:
        await message.answer(
            "❌ Название должно содержать минимум 3 символа.\n\n"
            "💡 <b>Совет:</b> Добавьте больше деталей к названию.\n"
            "Например: вместо «Сайт» напишите «Создать сайт-визитку для компании»",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(title=title)
    await state.set_state(TaskCreation.description)
    await message.answer(
        "✅ <b>Название сохранено!</b>\n\n"
        "📄 <b>Шаг 2: Описание задачи</b>\n\n"
        "💡 <b>Что включить в описание:</b>\n"
        "• Подробные требования к работе\n"
        "• Желаемый результат\n"
        "• Технические детали\n"
        "• Сроки выполнения\n"
        "• Дополнительные пожелания\n\n"
        "📝 <b>Пример хорошего описания:</b>\n"
        "«Нужно создать лендинг для интернет-магазина одежды. "
        "Сайт должен быть адаптивным, с корзиной покупок и формой заказа. "
        "Дизайн в стиле минимализм, цветовая схема - белый и черный. "
        "Нужно интегрировать платежную систему.»\n\n"
        "🎯 <b>Опишите вашу задачу подробно:</b>",
        parse_mode="HTML"
    )

@router.message(TaskCreation.description)
async def get_task_description(message: types.Message, state: FSMContext):
    """Получить описание задачи"""
    description = message.text.strip()
    
    if len(description) < 10:
        await message.answer(
            "❌ Описание должно содержать минимум 10 символов.\n\n"
            "💡 <b>Совет:</b> Добавьте больше деталей о том, что именно нужно сделать, "
            "какие требования к результату, какие технологии использовать.",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(description=description)
    await state.set_state(TaskCreation.budget)
    await message.answer(
        "✅ <b>Описание сохранено!</b>\n\n"
        "💰 <b>Шаг 3: Бюджет задачи</b>\n\n"
        "💡 <b>Как указать бюджет:</b>\n"
        "• Напишите сумму в рублях (например: 5000)\n"
        "• Или диапазон (например: 3000-8000)\n"
        "• Или отправьте 0, если бюджет не определен\n\n"
        "📊 <b>Примеры бюджетов:</b>\n"
        "• Лендинг: 5000-15000 ₽\n"
        "• Логотип: 2000-8000 ₽\n"
        "• Статья: 500-2000 ₽\n"
        "• Мобильное приложение: 50000-200000 ₽\n\n"
        "💸 <b>Укажите бюджет в рублях:</b>",
        parse_mode="HTML"
    )

@router.message(TaskCreation.budget)
async def get_task_budget(message: types.Message, state: FSMContext):
    """Получить бюджет задачи"""
    try:
        budget = float(message.text.strip())
        if budget < 0:
            await message.answer("❌ Бюджет не может быть отрицательным.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму.")
        return
    
    await state.update_data(budget=budget if budget > 0 else None)
    await state.set_state(TaskCreation.priority)
    await message.answer(
        "💰 Бюджет сохранен!\n\n"
        "Выберите приоритет задачи:",
        reply_markup=get_priority_keyboard()
    )

@router.callback_query(TaskCreation.priority, F.data.startswith("priority_"))
async def get_task_priority(callback: types.CallbackQuery, state: FSMContext):
    """Получить приоритет задачи"""
    priority = int(callback.data.split("_")[1])
    
    await state.update_data(priority=priority)
    await state.set_state(TaskCreation.tags)
    await callback.message.edit_text(
        "🎯 Приоритет выбран!\n\n"
        "Введите теги для задачи через запятую (например: веб-разработка, дизайн, срочно):"
    )

@router.message(TaskCreation.tags)
async def get_task_tags(message: types.Message, state: FSMContext):
    """Получить теги задачи"""
    tags_text = message.text.strip()
    tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
    
    await state.update_data(tags=tags)
    
    # Показываем итоговую информацию
    data = await state.get_data()
    
    summary = (
        "📋 <b>Итоговая информация о задаче:</b>\n\n"
        f"📝 <b>Название:</b> {data['title']}\n"
        f"📄 <b>Описание:</b> {data['description'][:100]}{'...' if len(data['description']) > 100 else ''}\n"
        f"💰 <b>Бюджет:</b> {data['budget'] or 'Не указан'} ₽\n"
        f"🎯 <b>Приоритет:</b> {data['priority']}\n"
        f"🏷️ <b>Теги:</b> {', '.join(data['tags']) if data['tags'] else 'Не указаны'}\n\n"
        "Создать задачу?"
    )
    
    await state.set_state(TaskCreation.confirmation)
    await message.answer(
        summary,
        reply_markup=get_confirmation_keyboard("task"),
        parse_mode="HTML"
    )

@router.callback_query(TaskCreation.confirmation, F.data == "confirm_task")
async def confirm_create_task(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Подтвердить создание задачи"""
    try:
        data = await state.get_data()
        
        task_service = TaskService()
        task = await task_service.create_task(
            creator_id=user.id,
            title=data["title"],
            description=data["description"],
            budget=data["budget"],
            priority=data["priority"],
            tags=data["tags"]
        )
        
        await state.clear()
        
        await callback.message.edit_text(
            f"✅ <b>Задача успешно создана!</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"🆔 <b>ID:</b> {task.id}\n"
            f"📊 <b>Статус:</b> {task.status.value}\n\n"
            "Задача добавлена в вашу доску.",
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML"
        )
        
        logger.info(f"Task created by user {user.id}: {task.id}")
        
    except Exception as e:
        logger.error(f"Error creating task for user {user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании задачи. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked)
        )

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    """Отменить действие"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено.",
        reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked)
    ) 

@router.callback_query(F.data == "tasks")
async def tasks_menu_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Все задачи"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_service = TaskService()
        tasks = await task_service.get_user_tasks(user.id)
        
        if not tasks:
            await callback.message.edit_text(
                "📋 <b>Все задачи</b>\n\n"
                "У вас пока нет задач.\n"
                "Создайте новую задачу!",
                reply_markup=get_tasks_menu_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Формируем список задач
        tasks_text = "📋 <b>Все задачи:</b>\n\n"
        for i, task in enumerate(tasks[:10], 1):  # Показываем первые 10
            status_emoji = {
                'open': '🟢',
                'in_progress': '🟡',
                'completed': '✅',
                'cancelled': '❌'
            }.get(task.status, '📝')
            
            priority_emoji = {
                1: '🟢',
                2: '🟡',
                3: '🟠',
                4: '🔴'
            }.get(task.priority, '⚪')
            
            tasks_text += (
                f"{i}. {status_emoji} <b>{task.title}</b>\n"
                f"   Приоритет: {priority_emoji} {task.priority}\n"
                f"   Статус: {task.status}\n"
                f"   Создана: {task.created_at.strftime('%d.%m.%Y')}\n\n"
            )
        
        if len(tasks) > 10:
            tasks_text += f"... и еще {len(tasks) - 10} задач"
        
        try:
            await callback.message.edit_text(
                tasks_text,
                reply_markup=get_tasks_menu_keyboard(),
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                # Игнорируем ошибку если сообщение не изменилось
                pass
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error showing tasks for user {user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке задач.",
            reply_markup=get_tasks_menu_keyboard()
        ) 

@router.callback_query(F.data.startswith("edit_task:"))
async def edit_task_colon_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Редактировать задачу" (с двоеточием)
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split(":")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для редактирования этой задачи!", show_alert=True)
            return
        
        edit_text = (
            f"✏️ <b>Редактирование задачи</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n"
            f"🎯 <b>Приоритет:</b> {task.priority}\n"
            f"📊 <b>Статус:</b> {task.status.value}\n\n"
            f"💡 <b>Для редактирования перейдите на сайт:</b>\n"
            f"🌐 <a href='http://localhost:3000/tasks/{task_id}/edit'>Редактировать задачу</a>"
        )
        
        from ..keyboards.task_keyboards import get_task_keyboard
        await callback.message.edit_text(
            edit_text,
            reply_markup=get_task_keyboard(task_id),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error editing task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("delete_task:"))
async def delete_task_colon_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Удалить задачу" (с двоеточием)
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split(":")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для удаления этой задачи!", show_alert=True)
            return
        
        # Показываем подтверждение удаления
        confirm_text = (
            f"🗑️ <b>Удаление задачи</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n\n"
            f"⚠️ <b>Внимание!</b>\n"
            f"Это действие нельзя отменить. Задача будет удалена навсегда.\n\n"
            f"Вы уверены, что хотите удалить эту задачу?"
        )
        
        from ..keyboards.main_keyboards import get_confirmation_keyboard
        await callback.message.edit_text(
            confirm_text,
            reply_markup=get_confirmation_keyboard("delete_task", task_id),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Завершить задачу"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split("_")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для завершения этой задачи!", show_alert=True)
            return
        
        # Завершаем задачу
        await task_service.update_task_status(task_id, TaskStatus.DONE)
        
        complete_text = (
            f"✅ <b>Задача завершена!</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n"
            f"📅 <b>Завершена:</b> {task.updated_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"🎉 <b>Поздравляем с завершением задачи!</b>"
        )
        
        await callback.message.edit_text(
            complete_text,
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("assign_task_"))
async def assign_task_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Назначить задачу"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split("_")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для назначения этой задачи!", show_alert=True)
            return
        
        assign_text = (
            f"👤 <b>Назначение задачи</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n\n"
            f"💡 <b>Для назначения исполнителя перейдите на сайт:</b>\n"
            f"🌐 <a href='http://localhost:3000/tasks/{task_id}/assign'>Назначить исполнителя</a>\n\n"
            f"Там вы сможете:\n"
            f"• Выбрать исполнителя из списка\n"
            f"• Просмотреть профили кандидатов\n"
            f"• Обсудить условия работы\n"
            f"• Назначить исполнителя"
        )
        
        await callback.message.edit_text(
            assign_text,
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True) 

@router.callback_query(F.data == "back_to_tasks")
async def back_to_tasks_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Назад к задачам"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_service = TaskService()
        tasks = await task_service.get_user_tasks(user.id)
        
        if not tasks:
            await callback.message.edit_text(
                "📋 <b>Мои задачи</b>\n\n"
                "У вас пока нет задач.\n"
                "Создайте новую задачу!",
                reply_markup=get_task_actions_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Формируем список задач
        tasks_text = "📋 <b>Мои задачи:</b>\n\n"
        for i, task in enumerate(tasks[:10], 1):  # Показываем первые 10
            status_emoji = {
                TaskStatus.TODO: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.DONE: "✅",
                TaskStatus.CANCELLED: "❌"
            }.get(task.status, "📝")
            
            tasks_text += (
                f"{i}. {status_emoji} <b>{task.title}</b>\n"
                f"   Статус: {task.status.value}\n"
                f"   Приоритет: {task.priority}\n"
                f"   Бюджет: {task.budget or 'Не указан'} ₽\n\n"
            )
        
        if len(tasks) > 10:
            tasks_text += f"... и еще {len(tasks) - 10} задач"
        
        await callback.message.edit_text(
            tasks_text,
            reply_markup=get_task_actions_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error showing tasks for user {user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке задач.",
            reply_markup=get_task_actions_keyboard()
        ) 

@router.callback_query(F.data.startswith("edit_task_"))
async def edit_task_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Редактировать задачу" (с подчеркиванием)
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split("_")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для редактирования этой задачи!", show_alert=True)
            return
        
        edit_text = (
            f"✏️ <b>Редактирование задачи</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n"
            f"🎯 <b>Приоритет:</b> {task.priority}\n"
            f"📊 <b>Статус:</b> {task.status.value}\n\n"
            f"💡 <b>Для редактирования перейдите на сайт:</b>\n"
            f"🌐 <a href='http://localhost:3000/tasks/{task_id}/edit'>Редактировать задачу</a>"
        )
        
        await callback.message.edit_text(
            edit_text,
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error editing task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("delete_task_"))
async def delete_task_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Удалить задачу" (с подчеркиванием)
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split("_")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для удаления этой задачи!", show_alert=True)
            return
        
        # Показываем подтверждение удаления
        confirm_text = (
            f"🗑️ <b>Удаление задачи</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n\n"
            f"⚠️ <b>Внимание!</b>\n"
            f"Это действие нельзя отменить. Задача будет удалена навсегда.\n\n"
            f"Вы уверены, что хотите удалить эту задачу?"
        )
        
        from ..keyboards.main_keyboards import get_confirmation_keyboard
        await callback.message.edit_text(
            confirm_text,
            reply_markup=get_confirmation_keyboard("delete_task", task_id),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Завершить задачу"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split("_")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для завершения этой задачи!", show_alert=True)
            return
        
        # Завершаем задачу
        await task_service.update_task_status(task_id, TaskStatus.DONE)
        
        complete_text = (
            f"✅ <b>Задача завершена!</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n"
            f"📅 <b>Завершена:</b> {task.updated_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"🎉 <b>Поздравляем с завершением задачи!</b>"
        )
        
        await callback.message.edit_text(
            complete_text,
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("assign_task_"))
async def assign_task_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Назначить задачу"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        task_id = int(callback.data.split("_")[-1])
        task_service = TaskService()
        task = await task_service.get_task_by_id(task_id)
        
        if not task:
            await callback.answer("❌ Задача не найдена!", show_alert=True)
            return
        
        if task.creator_id != user.id:
            await callback.answer("❌ У вас нет прав для назначения этой задачи!", show_alert=True)
            return
        
        assign_text = (
            f"👤 <b>Назначение задачи</b>\n\n"
            f"📝 <b>Название:</b> {task.title}\n"
            f"📄 <b>Описание:</b> {task.description[:100]}{'...' if len(task.description) > 100 else ''}\n"
            f"💰 <b>Бюджет:</b> {task.budget or 'Не указан'} ₽\n\n"
            f"💡 <b>Для назначения исполнителя перейдите на сайт:</b>\n"
            f"🌐 <a href='http://localhost:3000/tasks/{task_id}/assign'>Назначить исполнителя</a>\n\n"
            f"Там вы сможете:\n"
            f"• Выбрать исполнителя из списка\n"
            f"• Просмотреть профили кандидатов\n"
            f"• Обсудить условия работы\n"
            f"• Назначить исполнителя"
        )
        
        await callback.message.edit_text(
            assign_text,
            reply_markup=get_main_menu_keyboard(is_admin=user.role == 'admin' if user else False, is_linked=is_linked),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True) 