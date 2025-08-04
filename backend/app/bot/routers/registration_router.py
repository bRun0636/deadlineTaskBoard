import logging
import json
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from ..states.registration_states import Registration
from ..keyboards.registration_keyboards import (
    get_phone_keyboard, get_role_keyboard, get_country_keyboard,
    get_juridical_type_keyboard, get_payment_types_keyboard,
    get_prof_level_keyboard, get_notification_types_keyboard
)
from ..services.user_service import UserService
from app.models.user import UserRole, JuridicalType, PaymentType, NotificationType, User

router = Router(name="registration_router")
logger = logging.getLogger(__name__)

@router.message(Command("register"))
async def start_registration(message: types.Message, state: FSMContext, user: User):
    """Начать регистрацию"""
    if user and user.is_registered:
        await message.answer("✅ Вы уже зарегистрированы!")
        return
    
    await state.set_state(Registration.phone)
    await message.answer(
        "🔐 <b>Регистрация в Deadline Task Board</b>\n\n"
        "📱 <b>Шаг 1: Номер телефона</b>\n\n"
        "Для начала регистрации отправьте ваш номер телефона.\n"
        "💡 <b>Зачем нужен номер:</b>\n"
        "• Для связи с заказчиками\n"
        "• Для уведомлений о платежах\n"
        "• Для безопасности аккаунта\n\n"
        "🔒 <b>Ваши данные защищены и не передаются третьим лицам</b>",
        reply_markup=get_phone_keyboard(),
        parse_mode="HTML"
    )

@router.message(Registration.phone, F.contact)
async def get_phone_handler(message: types.Message, state: FSMContext, user: User):
    """Обработка номера телефона"""
    phone = message.contact.phone_number
    
    # Сохраняем номер телефона
    await state.update_data(phone=phone)
    
    # Переходим к выбору роли
    await state.set_state(Registration.role)
    await message.answer(
        "✅ <b>Номер телефона получен!</b>\n\n"
        "👤 <b>Шаг 2: Выберите вашу роль</b>\n\n"
        "💡 <b>Заказчик:</b>\n"
        "• Размещаете заказы и задачи\n"
        "• Выбираете исполнителей\n"
        "• Оплачиваете выполненную работу\n\n"
        "💡 <b>Исполнитель:</b>\n"
        "• Выполняете заказы и задачи\n"
        "• Получаете оплату за работу\n"
        "• Развиваете портфолио\n\n"
        "🔄 <b>Вы всегда можете изменить роль позже в настройках</b>",
        reply_markup=get_role_keyboard(),
        parse_mode="HTML"
    )

@router.message(Registration.phone)
async def handle_invalid_phone(message: types.Message):
    """Обработка некорректного ввода номера телефона"""
    await message.answer(
        "❌ Пожалуйста, используйте кнопку для отправки номера телефона."
    )

@router.callback_query(Registration.role, F.data.startswith("role_"))
async def get_role_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора роли"""
    role = callback.data.split("_")[1]
    
    # Сохраняем роль
    await state.update_data(role=role)
    
    # Переходим к выбору страны
    await state.set_state(Registration.country)
    try:
        await callback.message.edit_text(
            "✅ <b>Роль выбрана!</b>\n\n"
            "🌍 <b>Шаг 3: Выберите вашу страну</b>\n\n"
            "💡 <b>Зачем нужна страна:</b>\n"
            "• Для правильного расчета налогов\n"
            "• Для выбора способов оплаты\n"
            "• Для поиска местных исполнителей\n"
            "• Для соответствия законодательству\n\n"
            "🌐 <b>Выберите страну, где вы находитесь или работаете</b>",
            reply_markup=get_country_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.debug(f"Message edit failed: {e}")
    
    await callback.answer()

@router.callback_query(Registration.country, F.data.startswith("country_"))
async def get_country_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора страны"""
    country = callback.data.split("_")[1]
    
    # Сохраняем страну
    await state.update_data(country=country)
    
    # Переходим к выбору юридического статуса
    await state.set_state(Registration.juridical_type)
    try:
        await callback.message.edit_text(
            "✅ <b>Страна выбрана!</b>\n\n"
            "💼 <b>Шаг 4: Выберите юридический статус</b>\n\n"
            "💡 <b>Физическое лицо:</b>\n"
            "• Работаете как частное лицо\n"
            "• Подходит для фрилансеров\n"
            "• Простая регистрация\n\n"
            "💡 <b>ООО:</b>\n"
            "• Работаете через компанию\n"
            "• Нужны документы ООО\n"
            "• Подходит для бизнеса\n\n"
            "💡 <b>ИП:</b>\n"
            "• Индивидуальный предприниматель\n"
            "• Нужно свидетельство ИП\n"
            "• Подходит для самозанятых\n\n"
            "📋 <b>Выберите статус, с которым вы работаете</b>",
            reply_markup=get_juridical_type_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.debug(f"Message edit failed: {e}")
    
    await callback.answer()

@router.callback_query(Registration.juridical_type, F.data.startswith("juridical_"))
async def get_juridical_type_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора юридического статуса"""
    juridical_type = callback.data.split("_")[1]
    
    # Сохраняем юридический статус
    await state.update_data(juridical_type=juridical_type)
    
    # Переходим к выбору типов оплаты
    await state.set_state(Registration.payment_types)
    try:
        await callback.message.edit_text(
            "✅ <b>Юридический статус выбран!</b>\n\n"
            "💳 <b>Шаг 5: Выберите способы оплаты</b>\n\n"
            "💡 <b>Выберите все способы, которые вам подходят:</b>\n"
            "• Банковская карта - быстро и удобно\n"
            "• Наличные - для личных встреч\n"
            "• Банковский перевод - для крупных сумм\n"
            "• Криптовалюта - анонимно и современно\n\n"
            "💰 <b>Вы можете выбрать несколько способов</b>\n"
            "🔄 <b>Нажмите на способ, чтобы включить/выключить</b>",
            reply_markup=get_payment_types_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.debug(f"Message edit failed: {e}")
    
    await callback.answer()

@router.callback_query(Registration.payment_types, F.data.startswith("payment_toggle_"))
async def toggle_payment_type_handler(callback: types.CallbackQuery, state: FSMContext):
    """Переключение типа оплаты"""
    payment_type = callback.data.split("_")[2]
    
    # Получаем текущие выбранные типы
    data = await state.get_data()
    selected_types = data.get("payment_types", [])
    
    # Переключаем тип
    if payment_type in selected_types:
        selected_types.remove(payment_type)
    else:
        selected_types.append(payment_type)
    
    # Сохраняем обновленный список
    await state.update_data(payment_types=selected_types)
    
    # Обновляем клавиатуру
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_payment_types_keyboard(selected_types)
        )
    except Exception as e:
        logger.debug(f"Message edit failed (likely unchanged): {e}")
    
    await callback.answer()

@router.callback_query(Registration.payment_types, F.data == "payment_done")
async def payment_types_done_handler(callback: types.CallbackQuery, state: FSMContext):
    """Завершение выбора типов оплаты"""
    data = await state.get_data()
    payment_types = data.get("payment_types", [])
    
    if not payment_types:
        await callback.answer("❌ Выберите хотя бы один тип оплаты!", show_alert=True)
        return
    
    # Переходим к выбору уровня профессионализма
    await state.set_state(Registration.prof_level)
    try:
        await callback.message.edit_text(
            "✅ <b>Способы оплаты выбраны!</b>\n\n"
            "🎯 <b>Шаг 6: Выберите уровень профессионализма</b>\n\n"
            "💡 <b>Уровни:</b>\n"
            "🟢 <b>Junior</b> - начинающий специалист (0-1 год опыта)\n"
            "🟡 <b>Middle</b> - опытный специалист (1-3 года опыта)\n"
            "🟠 <b>Senior</b> - старший специалист (3+ лет опыта)\n"
            "🔴 <b>Expert</b> - эксперт в своей области (5+ лет опыта)\n\n"
            "📊 <b>Это поможет заказчикам оценить ваш опыт</b>\n"
            "🔄 <b>Вы всегда можете изменить уровень в профиле</b>",
            reply_markup=get_prof_level_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.debug(f"Message edit failed: {e}")
    
    await callback.answer()

@router.callback_query(Registration.prof_level, F.data.startswith("prof_level_"))
async def get_prof_level_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора уровня профессионализма"""
    prof_level = callback.data.split("_")[2]
    
    # Сохраняем уровень профессионализма
    await state.update_data(prof_level=prof_level)
    
    # Переходим к вводу навыков
    await state.set_state(Registration.skills)
    try:
        await callback.message.edit_text(
            "✅ <b>Уровень профессионализма выбран!</b>\n\n"
            "💪 <b>Шаг 7: Укажите ваши навыки</b>\n\n"
            "💡 <b>Напишите навыки через запятую:</b>\n"
            "• Языки программирования (Python, JavaScript, Java)\n"
            "• Технологии (React, Django, Docker)\n"
            "• Инструменты (Photoshop, Figma, Excel)\n"
            "• Языки (английский, испанский)\n"
            "• Специализации (SEO, SMM, аналитика)\n\n"
            "📝 <b>Примеры:</b>\n"
            "• Веб-разработка, JavaScript, React, Node.js\n"
            "• Дизайн, Photoshop, Figma, UI/UX\n"
            "• Копирайтинг, SEO, маркетинг, SMM\n\n"
            "🎯 <b>Укажите навыки, которые у вас есть</b>"
        )
    except Exception as e:
        logger.debug(f"Message edit failed: {e}")
    
    await callback.answer()

@router.message(Registration.skills)
async def get_skills_handler(message: types.Message, state: FSMContext):
    """Обработка ввода навыков"""
    skills_text = message.text.strip()
    skills_list = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
    
    if not skills_list:
        await message.answer(
            "❌ Пожалуйста, укажите хотя бы один навык.\n\n"
            "💡 <b>Примеры навыков:</b>\n"
            "• Веб-разработка, JavaScript, React\n"
            "• Дизайн, Photoshop, Figma\n"
            "• Копирайтинг, SEO, маркетинг\n"
            "• Мобильная разработка, iOS, Android\n"
            "• Аналитика данных, Python, SQL",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем навыки
    await state.update_data(skills=skills_list)
    
    # Переходим к вводу биографии
    await state.set_state(Registration.bio)
    await message.answer(
        "💪 Навыки сохранены!\n\n"
        "📝 <b>Теперь расскажите о себе (биография):</b>\n\n"
        "💡 <b>Что можно написать:</b>\n"
        "• Ваш опыт работы\n"
        "• Образование и сертификаты\n"
        "• Достижения и проекты\n"
        "• Почему вы хотите работать в этой сфере\n"
        "• Ваши сильные стороны\n\n"
        "📝 <b>Пример:</b>\n"
        "«Я веб-разработчик с 3-летним опытом. Создал более 20 сайтов для малого бизнеса. "
        "Специализируюсь на React и Node.js. Люблю создавать удобные и красивые интерфейсы.»",
        parse_mode="HTML"
    )

@router.message(Registration.bio)
async def get_bio_handler(message: types.Message, state: FSMContext):
    """Обработка ввода биографии"""
    bio = message.text.strip()
    
    if len(bio) < 10:
        await message.answer(
            "❌ Биография должна содержать минимум 10 символов.\n\n"
            "💡 <b>Совет:</b> Расскажите о своем опыте, образовании, достижениях или целях. "
            "Это поможет заказчикам лучше понять ваши возможности.",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем биографию
    await state.update_data(bio=bio)
    
    # Переходим к выбору уведомлений
    await state.set_state(Registration.notifications)
    await message.answer(
        "📝 Биография сохранена!\n\n"
        "🔔 <b>Выберите типы уведомлений:</b>\n\n"
        "💡 <b>Рекомендуем выбрать все типы для полного информирования:</b>\n"
        "• Новые задачи - узнаете о новых заказах\n"
        "• Обновления задач - изменения в ваших задачах\n"
        "• Сообщения - переписка с заказчиками\n"
        "• Платежи - информация о выплатах\n"
        "• Системные - важные уведомления от системы",
        reply_markup=get_notification_types_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(Registration.notifications, F.data.startswith("notification_toggle_"))
async def toggle_notification_handler(callback: types.CallbackQuery, state: FSMContext):
    """Переключение типа уведомления"""
    # Извлекаем тип уведомления из callback_data
    # callback_data имеет вид "notification_toggle_new_tasks"
    notification_type = callback.data.replace("notification_toggle_", "")
    
    # Получаем текущие выбранные типы
    data = await state.get_data()
    selected_types = data.get("notification_types", [])
    
    # Переключаем тип
    if notification_type in selected_types:
        selected_types.remove(notification_type)
    else:
        selected_types.append(notification_type)
    
    # Сохраняем обновленный список
    await state.update_data(notification_types=selected_types)
    
    # Обновляем клавиатуру
    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_notification_types_keyboard(selected_types)
        )
    except Exception as e:
        logger.debug(f"Message edit failed (likely unchanged): {e}")
    
    await callback.answer()

@router.callback_query(Registration.notifications, F.data == "registration_complete")
async def complete_registration_handler(callback: types.CallbackQuery, state: FSMContext, user: User):
    """Завершение регистрации"""
    try:
        # Получаем все данные регистрации
        data = await state.get_data()
        
        # Обновляем пользователя в базе данных
        user_service = UserService()
        await user_service.complete_registration(
            telegram_id=callback.from_user.id,
            registration_data=data
        )
        
        # Очищаем состояние
        await state.clear()
        
        try:
            await callback.message.edit_text(
                "🎉 <b>Регистрация завершена!</b>\n\n"
                "Добро пожаловать в Deadline Task Board!\n"
                "Теперь вы можете использовать все функции бота.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.debug(f"Message edit failed: {e}")
        
        logger.info(f"User {callback.from_user.id} completed registration")
        
    except Exception as e:
        logger.error(f"Error completing registration for user {callback.from_user.id}: {e}")
        try:
            await callback.message.edit_text(
                "❌ Произошла ошибка при завершении регистрации. Попробуйте позже."
            )
        except Exception as edit_error:
            logger.debug(f"Message edit failed: {edit_error}")
    
    await callback.answer() 