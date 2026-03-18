import json
from datetime import datetime
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardRemove

from config import bot, dp, ADMIN_ID, BUSINESS_DATA
from database import db
from yandex_gpt import ask_yandex_gpt, generate_welcome

# ==================== СОСТОЯНИЯ FSM ====================

class BookingStates(StatesGroup):
    choosing_service = State()
    entering_phone = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()

class FeedbackStates(StatesGroup):
    entering_rating = State()
    entering_comment = State()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_services_keyboard():
    kb = []
    for service in BUSINESS_DATA['services']:
        kb.append([KeyboardButton(text=f"{service['name']} - {service['price']}₽")])
    kb.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_dates_keyboard():
    kb = []
    for i in range(7):
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date = date.replace(day=date.day + i)
        date_str = date.strftime('%d.%m.%Y')
        day_name = date.strftime('%A')[:2]
        kb.append([KeyboardButton(text=f"{date_str} ({day_name})")])
    kb.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_times_keyboard():
    kb = []
    for hour in range(9, 21):
        time_str = f"{hour:02d}:00"
        kb.append([KeyboardButton(text=time_str)])
    kb.append([KeyboardButton(text="❌ Отмена")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📋 Услуги и цены")],
        [KeyboardButton(text="📝 Записаться")],
        [KeyboardButton(text="📅 Мои записи")],
        [KeyboardButton(text="📍 Контакты")],
        [KeyboardButton(text="❓ Частые вопросы")],
        [KeyboardButton(text="✍️ Оставить отзыв")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    """Начало работы"""
    welcome = await generate_welcome(message.from_user.first_name)
    text = f"""
👋 {welcome}

Я — нейро-ассистент салона красоты «{BUSINESS_DATA['business_name']}».
Я помогу записаться, узнать цены и ответить на вопросы.

Выберите действие из меню ниже:
    """
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(F.text == "📋 Услуги и цены")
async def show_services(message: types.Message):
    text = "📋 <b>Наши услуги и цены:</b>\n\n"
    for service in BUSINESS_DATA['services']:
        text += f"• {service['name']}: <b>{service['price']}₽</b> ({service['duration']} мин)\n"
    await message.answer(text)

@dp.message(F.text == "📍 Контакты")
async def show_contacts(message: types.Message):
    text = f"""
📍 <b>{BUSINESS_DATA['business_name']}</b>

🏠 Адрес: {BUSINESS_DATA['address']}
📞 Телефон: {BUSINESS_DATA['phone']}

🕒 Часы работы:
"""
    for day, hours in BUSINESS_DATA['work_hours'].items():
        text += f"   {day}: {hours}\n"
    await message.answer(text)

@dp.message(F.text == "❓ Частые вопросы")
async def show_faq(message: types.Message):
    text = "❓ <b>Часто задаваемые вопросы:</b>\n\n"
    for item in BUSINESS_DATA['faq']:
        text += f"<b>Вопрос:</b> {item['question']}\n"
        text += f"<b>Ответ:</b> {item['answer']}\n\n"
    await message.answer(text)

@dp.message(F.text == "📝 Записаться")
async def start_booking(message: types.Message, state: FSMContext):
    await state.set_state(BookingStates.choosing_service)
    await message.answer(
        "Выберите услугу:",
        reply_markup=get_services_keyboard()
    )

@dp.message(BookingStates.choosing_service)
async def process_service(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Запись отменена", reply_markup=get_main_keyboard())
        return
    
    # Ищем выбранную услугу
    selected_service = None
    for service in BUSINESS_DATA['services']:
        if service['name'] in message.text:
            selected_service = service
            break
    
    if not selected_service:
        await message.answer("Пожалуйста, выберите услугу из списка")
        return
    
    await state.update_data(selected_service=selected_service)
    await state.set_state(BookingStates.entering_phone)
    await message.answer(
        "📞 Введите ваш номер телефона для связи (например: +79991234567):",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(BookingStates.entering_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith('+') or len(phone) < 10:
        await message.answer("❌ Пожалуйста, введите корректный номер телефона в формате +79991234567")
        return
    
    await state.update_data(phone=phone)
    await state.set_state(BookingStates.choosing_date)
    await message.answer(
        "Выберите удобную дату:",
        reply_markup=get_dates_keyboard()
    )

@dp.message(BookingStates.choosing_date)
async def process_date(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Запись отменена", reply_markup=get_main_keyboard())
        return
    
    await state.update_data(booking_date=message.text.split()[0])
    await state.set_state(BookingStates.choosing_time)
    await message.answer(
        "Выберите удобное время:",
        reply_markup=get_times_keyboard()
    )

@dp.message(BookingStates.choosing_time)
async def process_time(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Запись отменена", reply_markup=get_main_keyboard())
        return
    
    data = await state.get_data()
    service = data['selected_service']
    
    text = f"""
✅ <b>Подтвердите запись:</b>

Услуга: {service['name']}
Цена: {service['price']}₽
Длительность: {service['duration']} мин
Дата: {data['booking_date']}
Время: {message.text}
Телефон: {data['phone']}

Всё верно?
    """
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, записать", callback_data="confirm_booking")],
        [InlineKeyboardButton(text="🔄 Заново", callback_data="restart_booking")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")]
    ])
    
    await state.update_data(booking_time=message.text)
    await state.set_state(BookingStates.confirming)
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service = data['selected_service']
    
    booking_id = db.create_booking(
        user_id=callback.from_user.id,
        username=callback.from_user.username or '',
        full_name=callback.from_user.full_name,
        phone=data['phone'],
        service_id=service['id'],
        service_name=service['name'],
        booking_date=data['booking_date'],
        booking_time=data['booking_time']
    )
    
    await callback.message.edit_text(
        f"✅ Запись подтверждена!\n\n"
        f"Номер записи: {booking_id}\n"
        f"Мы напомним о визите за 2 часа.\n"
        f"До встречи!"
    )
    await state.clear()
    await callback.message.answer("Выберите следующее действие:", reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "restart_booking")
async def restart_booking(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🔄 Начнём заново. Выберите услугу:")
    await start_booking(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Запись отменена.")
    await callback.message.answer("Выберите действие:", reply_markup=get_main_keyboard())
    await callback.answer()

@dp.message(F.text == "📅 Мои записи")
async def show_my_bookings(message: types.Message):
    bookings = db.get_user_bookings(message.from_user.id)
    
    if not bookings:
        await message.answer("У вас пока нет активных записей.")
        return
    
    text = "📅 <b>Ваши записи:</b>\n\n"
    for booking in bookings:
        text += f"🆔 Запись №{booking[0]}\n"
        text += f"💇 Услуга: {booking[6]}\n"
        text += f"📆 Дата: {booking[7]} в {booking[8]}\n"
        text += f"📞 Телефон: {booking[4]}\n"
        text += f"[Отменить](/cancel_{booking[0]})\n"
        text += "—\n"
    
    await message.answer(text)

@dp.message(F.text == "✍️ Оставить отзыв")
async def start_feedback(message: types.Message, state: FSMContext):
    await state.set_state(FeedbackStates.entering_rating)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(i)) for i in range(1, 6)]],
        resize_keyboard=True
    )
    await message.answer(
        "Оцените нашу работу от 1 до 5:",
        reply_markup=kb
    )

@dp.message(FeedbackStates.entering_rating)
async def process_rating(message: types.Message, state: FSMContext):
    if message.text not in ['1', '2', '3', '4', '5']:
        await message.answer("Пожалуйста, выберите оценку от 1 до 5")
        return
    
    await state.update_data(rating=int(message.text))
    await state.set_state(FeedbackStates.entering_comment)
    await message.answer(
        "Напишите ваш отзыв (можно оставить пустым, отправив /skip):",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(FeedbackStates.entering_comment)
async def process_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text if message.text != '/skip' else ''
    
    db.save_feedback(
        user_id=message.from_user.id,
        username=message.from_user.username or '',
        rating=data['rating'],
        comment=comment
    )
    
    await message.answer("✅ Спасибо за ваш отзыв!")
    await state.clear()

@dp.message(F.text)
async def handle_unknown(message: types.Message):
    """Обрабатывает неизвестные сообщения через YandexGPT"""
    await bot.send_chat_action(message.chat.id, action="typing")
    
    context = f"""
Клиент написал: "{message.text}"

Информация о салоне:
Название: {BUSINESS_DATA['business_name']}
Адрес: {BUSINESS_DATA['address']}
Телефон: {BUSINESS_DATA['phone']}
Часы работы: {BUSINESS_DATA['work_hours']}
Услуги: {BUSINESS_DATA['services']}
Частые вопросы: {BUSINESS_DATA['faq']}

Ответь клиенту вежливо и полезно. Если вопрос не относится к услугам салона, предложи связаться с администратором.
    """
    
    response = await ask_yandex_gpt(context)
    await message.answer(response)
