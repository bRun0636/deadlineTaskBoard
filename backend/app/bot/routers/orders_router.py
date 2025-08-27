import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from ..keyboards.main_keyboards import (
    get_main_menu_keyboard, get_orders_menu_keyboard,
    get_order_actions_keyboard, get_confirmation_keyboard
)
from ..services.user_service import UserService
from ..services.order_service import OrderService
from app.models.user import User
from app.models.order import OrderStatus
from app.models.proposal import ProposalStatus

router = Router(name="orders_router")
logger = logging.getLogger(__name__)

@router.message(Command("orders"))
async def show_orders_menu(message: types.Message, user: User):
    """Показать меню заказов"""
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы должны быть зарегистрированы для работы с заказами.\n"
            "Используйте /register для регистрации."
        )
        return
    
    await message.answer(
        "📊 <b>Управление заказами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_orders_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "orders")
async def show_orders_menu_handler(callback: types.CallbackQuery, user: User):
    """Показать меню заказов"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📊 <b>Управление заказами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_orders_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "my_orders")
async def show_my_orders(callback: types.CallbackQuery, user: User):
    """Показать мои заказы"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Получаем реальные данные из базы
        from ..services.order_service import OrderService
        order_service = OrderService()
        orders = await order_service.get_user_orders(user.id)
        
        if not orders:
            orders_text = "📦 <b>Мои заказы:</b>\n\n"
            orders_text += "📭 У вас пока нет заказов.\n"
            orders_text += "Создайте первый заказ, чтобы начать работу!"
        else:
            orders_text = f"📦 <b>Мои заказы ({len(orders)}):</b>\n\n"
            
            for i, order in enumerate(orders, 1):
                # Определяем статус и эмодзи
                status_emoji = {
                    OrderStatus.OPEN: '🟢',
                    OrderStatus.IN_PROGRESS: '🟡', 
                    OrderStatus.COMPLETED: '✅',
                    OrderStatus.CANCELLED: '❌'
                }.get(order.status, '❓')
                
                status_text = {
                    OrderStatus.OPEN: 'Открыт',
                    OrderStatus.IN_PROGRESS: 'В работе',
                    OrderStatus.COMPLETED: 'Завершен', 
                    OrderStatus.CANCELLED: 'Отменен'
                }.get(order.status, 'Неизвестно')
                
                # Форматируем дату
                created_date = order.created_at.strftime("%d.%m.%Y") if order.created_at else "Неизвестно"
                
                # Форматируем бюджет
                budget_text = f"{order.budget:,.0f} ₽" if order.budget else "Не указан"
                
                orders_text += f"{i}. {status_emoji} <b>{order.title}</b>\n"
                orders_text += f"   Бюджет: {budget_text}\n"
                orders_text += f"   Статус: {status_text}\n"
                orders_text += f"   Создан: {created_date}\n\n"
        
        from ..utils.message_utils import safe_edit_message
        
        success = await safe_edit_message(
            message=callback.message,
            text=orders_text,
            reply_markup=get_orders_menu_keyboard(),
            parse_mode="HTML"
        )
        
        if not success:
            await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error showing user orders: {e}")
        await callback.answer("❌ Ошибка при получении заказов", show_alert=True)

@router.callback_query(F.data == "available_orders")
async def show_available_orders(callback: types.CallbackQuery, user: User):
    """Показать доступные заказы"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Получаем реальные данные из базы
        from ..services.order_service import OrderService
        order_service = OrderService()
        orders = await order_service.get_available_orders()
        
        if not orders:
            orders_text = "🔍 <b>Доступные заказы:</b>\n\n"
            orders_text += "📭 Пока нет доступных заказов.\n"
            orders_text += "Заказы появятся, когда заказчики их создадут."
        else:
            orders_text = f"🔍 <b>Доступные заказы ({len(orders)}):</b>\n\n"
            
            for i, order in enumerate(orders, 1):
                # Получаем имя заказчика
                creator_name = order.creator.display_name if order.creator else "Неизвестно"
                
                # Форматируем дату
                created_date = order.created_at.strftime("%d.%m.%Y") if order.created_at else "Неизвестно"
                
                # Форматируем бюджет
                budget_text = f"{order.budget:,.0f} ₽" if order.budget else "Не указан"
                
                orders_text += f"{i}. <b>{order.title}</b>\n"
                orders_text += f"   Бюджет: {budget_text}\n"
                orders_text += f"   Заказчик: {creator_name}\n"
                orders_text += f"   Создан: {created_date}\n\n"
        
        from ..utils.message_utils import safe_edit_message
        
        success = await safe_edit_message(
            message=callback.message,
            text=orders_text,
            reply_markup=get_orders_menu_keyboard(),
            parse_mode="HTML"
        )
        
        if not success:
            await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error showing available orders: {e}")
        await callback.answer("❌ Ошибка при получении заказов", show_alert=True)

@router.callback_query(F.data == "create_order")
async def create_order_handler(callback: types.CallbackQuery, user: User):
    """Обработчик создания заказа"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Проверяем роль пользователя
    if user.role != 'customer' and user.role != 'admin':
        await callback.answer("❌ Только заказчики могут создавать заказы!", show_alert=True)
        return
    
    # Показываем инструкцию по созданию заказа
    order_text = (
        "➕ <b>Создание нового заказа</b>\n\n"
        "💡 <b>Как создать заказ:</b>\n"
        "1. Перейдите на сайт: deadline-task-board.com\n"
        "2. Войдите в свой аккаунт\n"
        "3. Нажмите 'Создать заказ'\n"
        "4. Заполните форму:\n"
        "   • Название заказа\n"
        "   • Описание работы\n"
        "   • Бюджет\n"
        "   • Срок выполнения\n"
        "   • Категория\n"
        "5. Нажмите 'Опубликовать'\n\n"
        "📋 <b>Требования к заказу:</b>\n"
        "• Четкое описание задачи\n"
        "• Реалистичный бюджет\n"
        "• Достаточный срок\n"
        "• Прикрепленные файлы (если нужно)\n\n"
        "🌐 <b>Создать заказ на сайте</b>\n"
        "Используйте веб-версию для удобного создания заказов."
    )
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=order_text,
        reply_markup=get_orders_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "my_proposals")
async def show_my_proposals(callback: types.CallbackQuery, user: User):
    """Показать мои предложения"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Получаем реальные данные из базы
        from ..services.order_service import OrderService
        order_service = OrderService()
        proposals = await order_service.get_user_proposals(user.id)
        
        if not proposals:
            proposals_text = "💼 <b>Мои предложения:</b>\n\n"
            proposals_text += "📭 У вас пока нет предложений.\n"
            proposals_text += "Отправьте предложения по доступным заказам!"
        else:
            proposals_text = f"💼 <b>Мои предложения ({len(proposals)}):</b>\n\n"
            
            for i, proposal in enumerate(proposals, 1):
                # Определяем статус и эмодзи
                status_emoji = {
                    'pending': '⏳',
                    'accepted': '✅',
                    'rejected': '❌',
                    'withdrawn': '🔄'
                }.get(proposal.status, '❓')
                
                status_text = {
                    'pending': 'На рассмотрении',
                    'accepted': 'Принято',
                    'rejected': 'Отклонено',
                    'withdrawn': 'Отозвано'
                }.get(proposal.status, 'Неизвестно')
                
                # Форматируем дату
                created_date = proposal.created_at.strftime("%d.%m.%Y") if proposal.created_at else "Неизвестно"
                
                # Форматируем цену
                price_text = f"{proposal.price:,.0f} ₽" if proposal.price else "Не указана"
                
                # Получаем название заказа
                order_title = proposal.order.title if proposal.order else "Заказ удален"
                
                proposals_text += f"{i}. {status_emoji} <b>{order_title}</b>\n"
                proposals_text += f"   Моя цена: {price_text}\n"
                proposals_text += f"   Статус: {status_text}\n"
                proposals_text += f"   Отправлено: {created_date}\n\n"
        
        from ..utils.message_utils import safe_edit_message
        
        success = await safe_edit_message(
            message=callback.message,
            text=proposals_text,
            reply_markup=get_orders_menu_keyboard(),
            parse_mode="HTML"
        )
        
        if not success:
            await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error showing user proposals: {e}")
        await callback.answer("❌ Ошибка при получении предложений", show_alert=True)

@router.callback_query(F.data == "order_statistics")
async def show_order_statistics(callback: types.CallbackQuery, user: User):
    """Показать статистику заказов"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Получаем реальные данные из базы
        from ..services.order_service import OrderService
        order_service = OrderService()
        stats = await order_service.get_order_statistics(user.id)
        
        # Получаем детальную статистику по статусам
        orders = await order_service.get_user_orders(user.id)
        
        # Подсчитываем заказы по статусам
        status_counts = {}
        for order in orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Форматируем статистику
        stats_text = "📈 <b>Статистика заказов</b>\n\n"
        stats_text += f"📦 Всего заказов: {stats['total_orders']}\n"
        stats_text += f"💼 Всего предложений: {stats['total_proposals']}\n"
        stats_text += f"✅ Принятых предложений: {stats['accepted_proposals']}\n"
        stats_text += f"❌ Отклоненных предложений: {stats['rejected_proposals']}\n"
        stats_text += f"💰 Общий заработок: {stats['total_earnings']:,.0f} ₽\n\n"
        
        if status_counts:
            stats_text += "📊 <b>По статусам заказов:</b>\n"
            status_names = {
                'open': 'Открытые',
                'in_progress': 'В работе',
                'completed': 'Завершенные',
                'cancelled': 'Отмененные'
            }
            
            for status, count in status_counts.items():
                status_name = status_names.get(status, status)
                stats_text += f"• {status_name}: {count} заказ(ов)\n"
        else:
            stats_text += "📊 <b>По статусам заказов:</b>\n"
            stats_text += "• Пока нет заказов\n"
        
        # Вычисляем эффективность
        if stats['total_proposals'] > 0:
            acceptance_rate = (stats['accepted_proposals'] / stats['total_proposals']) * 100
            stats_text += f"\n📈 <b>Эффективность:</b>\n"
            stats_text += f"• Процент принятия предложений: {acceptance_rate:.1f}%\n"
        
        if stats['total_orders'] > 0:
            avg_budget = sum(order.budget for order in orders if order.budget) / len([o for o in orders if o.budget])
            stats_text += f"• Средняя стоимость заказа: {avg_budget:,.0f} ₽\n"
        
        from ..utils.message_utils import safe_edit_message
        
        success = await safe_edit_message(
            message=callback.message,
            text=stats_text,
            reply_markup=get_orders_menu_keyboard(),
            parse_mode="HTML"
        )
        
        if not success:
            await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error showing order statistics: {e}")
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)

@router.callback_query(F.data == "back_to_orders")
async def back_to_orders_menu(callback: types.CallbackQuery, user: User):
    """Вернуться в меню заказов"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📊 <b>Управление заказами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_orders_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("edit_order_"))
async def edit_order_handler(callback: types.CallbackQuery, user: User):
    """Редактирование заказа"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        order_id = int(callback.data.replace("edit_order_", ""))
        
        # Получаем заказ
        from ..services.order_service import OrderService
        order_service = OrderService()
        order = await order_service.get_order_by_id(order_id)
        
        if not order:
            await callback.answer("❌ Заказ не найден!", show_alert=True)
            return
        
        # Проверяем права на редактирование
        if order.creator_id != user.id and user.role != UserRole.ADMIN:
            await callback.answer("❌ У вас нет прав на редактирование этого заказа!", show_alert=True)
            return
        
        # Показываем информацию о заказе для редактирования
        edit_text = (
            "✏️ <b>Редактирование заказа</b>\n\n"
            f"📝 <b>Название:</b> {order.title}\n"
            f"📄 <b>Описание:</b> {order.description[:100]}...\n"
            f"💰 <b>Бюджет:</b> {order.budget:,} ₽\n"
            f"📅 <b>Срок:</b> {order.deadline.strftime('%d.%m.%Y')}\n"
            f"🏷️ <b>Статус:</b> {order.status}\n\n"
            "Выберите, что хотите изменить:"
        )
        
        from ..keyboards.order_keyboards import get_order_edit_keyboard
        await callback.message.edit_text(
            edit_text,
            reply_markup=get_order_edit_keyboard(order_id),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error editing order: {e}")
        await callback.answer("❌ Ошибка при редактировании заказа", show_alert=True)


@router.callback_query(F.data.startswith("delete_order_"))
async def delete_order_handler(callback: types.CallbackQuery, user: User):
    """Удаление заказа"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        order_id = int(callback.data.replace("delete_order_", ""))
        
        # Получаем заказ
        from ..services.order_service import OrderService
        order_service = OrderService()
        order = await order_service.get_order_by_id(order_id)
        
        if not order:
            await callback.answer("❌ Заказ не найден!", show_alert=True)
            return
        
        # Проверяем права на удаление
        if order.creator_id != user.id and user.role != UserRole.ADMIN:
            await callback.answer("❌ У вас нет прав на удаление этого заказа!", show_alert=True)
            return
        
        # Показываем подтверждение удаления
        confirm_text = (
            "🗑️ <b>Удаление заказа</b>\n\n"
            f"📝 <b>Название:</b> {order.title}\n"
            f"💰 <b>Бюджет:</b> {order.budget:,} ₽\n\n"
            "⚠️ <b>Внимание!</b> Это действие нельзя отменить.\n"
            "Все предложения к заказу также будут удалены.\n\n"
            "Вы уверены, что хотите удалить этот заказ?"
        )
        
        from ..keyboards.order_keyboards import get_confirmation_keyboard
        await callback.message.edit_text(
            confirm_text,
            reply_markup=get_confirmation_keyboard("delete_order", order_id),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error deleting order: {e}")
        await callback.answer("❌ Ошибка при удалении заказа", show_alert=True)


@router.callback_query(F.data.startswith("confirm_delete_order_"))
async def confirm_delete_order_handler(callback: types.CallbackQuery, user: User):
    """Подтверждение удаления заказа"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        order_id = int(callback.data.replace("confirm_delete_order_", ""))
        
        # Удаляем заказ
        from ..services.order_service import OrderService
        order_service = OrderService()
        success = await order_service.delete_order(order_id, user.id)
        
        if success:
            await callback.message.edit_text(
                "✅ <b>Заказ успешно удален!</b>\n\n"
                "Заказ и все связанные с ним предложения были удалены из системы.",
                reply_markup=get_orders_menu_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ Не удалось удалить заказ", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error confirming delete order: {e}")
        await callback.answer("❌ Ошибка при удалении заказа", show_alert=True)


@router.callback_query(F.data.startswith("complete_order_"))
async def complete_order_handler(callback: types.CallbackQuery, user: User):
    """Завершение заказа"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        order_id = int(callback.data.replace("complete_order_", ""))
        
        # Получаем заказ
        from ..services.order_service import OrderService
        order_service = OrderService()
        order = await order_service.get_order_by_id(order_id)
        
        if not order:
            await callback.answer("❌ Заказ не найден!", show_alert=True)
            return
        
        # Проверяем права на завершение
        if order.creator_id != user.id and user.role != UserRole.ADMIN:
            await callback.answer("❌ У вас нет прав на завершение этого заказа!", show_alert=True)
            return
        
        # Проверяем, что заказ в работе
        if order.status != "in_progress":
            await callback.answer("❌ Можно завершить только заказы в работе!", show_alert=True)
            return
        
        # Завершаем заказ
        success = await order_service.complete_order(order_id, user.id)
        
        if success:
            await callback.message.edit_text(
                "✅ <b>Заказ успешно завершен!</b>\n\n"
                f"📝 <b>Название:</b> {order.title}\n"
                f"💰 <b>Бюджет:</b> {order.budget:,} ₽\n\n"
                "Заказ переведен в статус 'Завершен'.",
                reply_markup=get_orders_menu_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ Не удалось завершить заказ", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error completing order: {e}")
        await callback.answer("❌ Ошибка при завершении заказа", show_alert=True)


@router.callback_query(F.data.startswith("order_proposals_"))
async def show_order_proposals_handler(callback: types.CallbackQuery, user: User):
    """Показать предложения к заказу"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        order_id = int(callback.data.replace("order_proposals_", ""))
        
        # Получаем заказ и предложения
        from ..services.order_service import OrderService
        order_service = OrderService()
        order = await order_service.get_order_by_id(order_id)
        proposals = await order_service.get_order_proposals(order_id)
        
        if not order:
            await callback.answer("❌ Заказ не найден!", show_alert=True)
            return
        
        # Проверяем права на просмотр предложений
        if order.creator_id != user.id and user.role != UserRole.ADMIN:
            await callback.answer("❌ У вас нет прав на просмотр предложений к этому заказу!", show_alert=True)
            return
        
        if not proposals:
            await callback.message.edit_text(
                "📋 <b>Предложения к заказу</b>\n\n"
                f"📝 <b>Заказ:</b> {order.title}\n\n"
                "💼 <b>Предложения:</b>\n"
                "Пока нет предложений к этому заказу.\n\n"
                "Исполнители могут оставить предложения, если заказ открыт.",
                reply_markup=get_orders_menu_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Формируем список предложений
        proposals_text = (
            "📋 <b>Предложения к заказу</b>\n\n"
            f"📝 <b>Заказ:</b> {order.title}\n"
            f"💰 <b>Бюджет:</b> {order.budget:,} ₽\n\n"
            f"💼 <b>Предложения ({len(proposals)}):</b>\n\n"
        )
        
        for i, proposal in enumerate(proposals[:10], 1):  # Показываем первые 10
            executor_name = proposal.executor.full_name or proposal.executor.username or "Неизвестно"
            proposals_text += (
                f"{i}. <b>{executor_name}</b>\n"
                f"   💰 Цена: {proposal.price:,} ₽\n"
                f"   📅 Срок: {proposal.deadline.strftime('%d.%m.%Y')}\n"
                f"   📝 Комментарий: {proposal.comment[:50]}...\n\n"
            )
        
        if len(proposals) > 10:
            proposals_text += f"... и еще {len(proposals) - 10} предложений\n\n"
        
        proposals_text += "Выберите предложение для принятия или отклонения."
        
        # Создаем клавиатуру с предложениями
        from ..keyboards.order_keyboards import get_proposals_keyboard
        await callback.message.edit_text(
            proposals_text,
            reply_markup=get_proposals_keyboard(order_id, proposals),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error showing order proposals: {e}")
        await callback.answer("❌ Ошибка при получении предложений", show_alert=True)


@router.callback_query(F.data.startswith("accept_proposal_"))
async def accept_proposal_handler(callback: types.CallbackQuery, user: User):
    """Принятие предложения к заказу"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Парсим данные: accept_proposal_{order_id}_{proposal_id}
        parts = callback.data.split("_")
        order_id = int(parts[2])
        proposal_id = int(parts[3])
        
        # Принимаем предложение
        from ..services.order_service import OrderService
        order_service = OrderService()
        success = await order_service.accept_proposal(proposal_id, user.id)
        
        if success:
            await callback.answer("✅ Предложение принято! Заказ переведен в работу.", show_alert=True)
            
            # Возвращаемся к списку заказов
            await callback.message.edit_text(
                "✅ <b>Предложение принято!</b>\n\n"
                "Заказ переведен в статус 'В работе'.\n"
                "Исполнитель уведомлен о принятии предложения.",
                reply_markup=get_orders_menu_keyboard(),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ Не удалось принять предложение", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error accepting proposal: {e}")
        await callback.answer("❌ Ошибка при принятии предложения", show_alert=True)


@router.callback_query(F.data.startswith("reject_proposal_"))
async def reject_proposal_handler(callback: types.CallbackQuery, user: User):
    """Отклонение предложения к заказу"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Парсим данные: reject_proposal_{order_id}_{proposal_id}
        parts = callback.data.split("_")
        order_id = int(parts[2])
        proposal_id = int(parts[3])
        
        # Отклоняем предложение
        from ..services.order_service import OrderService
        order_service = OrderService()
        success = await order_service.reject_proposal(proposal_id, user.id)
        
        if success:
            await callback.answer("❌ Предложение отклонено", show_alert=True)
            
            # Возвращаемся к списку предложений
            await show_order_proposals_handler(callback, user)
        else:
            await callback.answer("❌ Не удалось отклонить предложение", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error rejecting proposal: {e}")
        await callback.answer("❌ Ошибка при отклонении предложения", show_alert=True) 