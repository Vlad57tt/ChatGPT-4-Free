import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters.state import State, StatesGroup

import openai

TOKEN = '5820633185:AAFzKVEf4aK_oVC1mkdLdtOzpwIs7-MXlco'
openai.api_key = 'Q2zpQWk3aJS_8Z5xw38J4W0aL_a8BdjB4L67tzFnJ0U'
openai.api_base = "https://chimeragpt.adventblocks.cc/v1"

owner_id = 1372715395

admin_ids = []

message_for_guest = "У вас нет прав для выполнения этой команды.\nЦена: 25 RUB/Месяц\nДля приобретения прав пожалуйста напишите /dev_info"

available_models = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-instant-100k",
        "claude-instant",
        "gpt-4-poe",
        "gpt-3.5-turbo-poe",
]


logging.basicConfig(level=logging.INFO)

class ImagePrompt(StatesGroup):
    waiting_for_text = State()
  

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_states = {}  # Dictionary to store user states and conversation history
def check_id(user_id):
  if user_id in admin_ids or user_id == owner_id:
    return True
  else:
    return False

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    if not check_id(user_id):
        await message.answer(message_for_guest)
        return
    user = message.from_user
    user_states[user_id] = {'model': None, 'button_sent': False, 'conversation': []}
    await message.answer(f"Привет, {user.first_name}! Я много-модельный чат бот, я создан начинающим кодером Vladdra C.", reply_markup=get_start_dialog_keyboard())

@dp.message_handler(commands=['dev_info'])
async def send_dev_info(message: types.Message):
    from_u = message.from_user
    user_id, first_name, username, language_code, is_premium = from_u.id, from_u.first_name, from_u.username, from_u.language_code, from_u.is_premium

    await message.reply(f"Ваш ID: {user_id}\nДля покупки прав обратитесь к @trainee_developer и сообщите ваш ID")

    await bot.send_message(owner_id, f"Новое сообщение по команде /dev_info:\n➖➖➖➖➖➖➖➖➖➖➖➖\nUser ID: {user_id}\nFirst Name: {first_name}\nUsername: @{username}\nLanguage Code: {language_code}\nTelegram Premium: {is_premium}\n➖➖➖➖➖➖➖➖➖➖➖➖")

@dp.message_handler(lambda message: message.text.lower() == 'начать диалог')
async def handle_start_dialog(message: types.Message):
    user_id = message.from_user.id
    if not check_id(user_id):
        await message.answer(message_for_guest)
        return
    user = message.from_user
    if user_id in user_states:
        user_data = user_states[user_id]
        if user_data['model']:
            await message.reply('Для начала завершите диалог.')
        else:
            model_keyboard = types.InlineKeyboardMarkup(row_width=1)
            model_buttons = [types.InlineKeyboardButton(model, callback_data=model) for model in available_models]
            model_keyboard.add(*model_buttons)
            await message.reply(f'{user.first_name}, пожалуйста, выберите модель:', reply_markup=model_keyboard)
    else:
        user_states[user_id] = {'model': None, 'button_sent': False, 'conversation': []}
        model_keyboard = types.InlineKeyboardMarkup(row_width=1)
        model_buttons = [types.InlineKeyboardButton(model, callback_data=model) for model in available_models]
        model_keyboard.add(*model_buttons)
        await message.answer(f'{user.first_name}, пожалуйста, выберите модель:', reply_markup=model_keyboard)

@dp.callback_query_handler(lambda query: query.data in available_models)
async def select_model(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    model = callback_query.data
    user_states[user_id] = {'model': model, 'button_sent': False, 'conversation': []}  # Store the selected model for the user
    await callback_query.answer()
    await callback_query.message.edit_text(f'Выбранная модель: {model}.\nОтправьте сообщение, чтобы начать диалог.')

@dp.message_handler(commands=("view_admins"))
async def view_admins(message: types.Message):
    if message.from_user.id == owner_id:
        admins_list = "\n".join(str(admin_id) for admin_id in admin_ids)

        await message.reply(f"Список admin_ids:\n{admins_list}")
    else:
        await message.reply('Данная команда не доступна. ')

@dp.message_handler(commands=("remove_admin"))
async def remove_admin(message: types.Message):
    if message.from_user.id == owner_id:
        try:
            admin_id = int(message.get_args())

        except (ValueError, TypeError):

            await message.reply("Укажите правильный admin_id для удаления.")
            return
        if admin_id in admin_ids:

            admin_ids.remove(admin_id)

            await message.reply(f"ID: {admin_id} удален из списка.")

        else:
            await message.reply(f"ID: {admin_id} не найден в списке.")

    else:
        await message.reply('Данная команда не доступна. ')

@dp.message_handler(commands=['add_admin'])
async def add_admin(message: types.Message):
    if message.from_user.id != owner_id:
        await message.reply("Данная команда не доступна. ")
        return
    if len(message.text.split()) > 1:
        new_admin_id = int(message.text.split()[1])

        if new_admin_id not in admin_ids:
          admin_ids.append(new_admin_id)
          try:
            await bot.send_message(new_admin_id,"Ваша подписка успешно активирована!")
            mes = "Администратор успешно добавлен и получил сообщение об активации"
          except:
            mes = "Администратор успешно добавлен но не получил сообщение об активации"
          await message.reply(mes)

        else:
            await message.reply("Этот пользователь уже является администратором.")

    else:
        await message.reply("Укажите ID пользователя, которого нужно добавить.")
      
@dp.message_handler(commands=('image'))
async def cmd_image(message: types.Message):
    user_id = message.from_user.id
    if not check_id(user_id):
        await message.answer(message_for_guest)
        return
    await message.answer("Введите текст для промпта:")
    # переводим бота в состояние ожидания текста от пользователя
    await ImagePrompt.waiting_for_text.set()


@dp.message_handler(state=ImagePrompt.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    try:
        prompt_text = message.text
        response = openai.Image.create(
            prompt=prompt_text,
            n=2,
            size="1024x1024"
        )
        for image in response['data']:
            await bot.send_photo(message.chat.id, photo=image['url'])
        await state.finish()
    except:
        error_message = "Произошла ошибка при создании изображения"
        await message.answer(error_message)
      
@dp.message_handler(lambda message: message.text.lower() == 'завершить диалог')
async def cancel(message: types.Message):
    user_id = message.from_user.id
    if not check_id(user_id):
        await message.answer(message_for_guest)
        return
    user_data = user_states.get(user_id)
    if user_data and user_data.get('button_sent'):
        user_states[user_id] = {'model': None, 'button_sent': False, 'conversation': []}  # Clear the user's selected model and conversation history
        await message.answer('Диалог завершен. Вы можете начать новый диалог, нажав кнопку "Начать диалог".', reply_markup=get_start_dialog_keyboard())
    else:
        await message.reply('Сейчас нет активного диалога.')

# Обработчик всех текстовых сообщений
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def chat_message(message: types.Message):
    user_id = message.from_user.id
    if not check_id(user_id):
        await message.answer(message_for_guest)
        return
    user_data = user_states.get(user_id, {})
    model = user_data.get('model')
    if model:
        conversation = user_data['conversation']
        conversation.append({'role': 'user', 'content': message.text})
        try:
            # Add user message to conversation and handle API response
            response = openai.ChatCompletion.create(model=model, messages=conversation)
            ai_response = response.choices[0].message['content']

            # Отправляем ответ всем участникам чата
            await message.reply(ai_response)

            if not user_data.get('button_sent', False):
                cancel_button = KeyboardButton("Завершить диалог")
                cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)
                await message.answer('Вы можете закончить диалог, нажав кнопку "Завершить диалог".', reply_markup=cancel_markup)
                user_states[user_id]['button_sent'] = True
        except:
          await message.answer("Произошла ошибка при обработке вашего запроса.")

def get_start_dialog_keyboard():
    start_button = KeyboardButton("Начать диалог")
    start_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(start_button)
    return start_markup

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
