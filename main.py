import asyncio
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import openai


class ImagePrompt(StatesGroup):
    waiting_for_text = State()

model = "gpt-3.5-turbo" #Standart model

openai.api_base = "https://chimeragpt.adventblocks.cc/v1"
  
openai.api_key = "Q2zpQWk3Yan_Z5xw80b4W0aL_ehjwNsbzFnJ0U" #your api chimera key from discord

TOKEN = "6176486575:AAEQRanMuGyolp05bHpOKalb0sT71uMhwOdk" #your api key bot tg


owner_id = 1372715395 # your id, get your id @getmyid_bot

admin_ids = []

message_for_guest = "У вас нет прав для выполнения этой команды.\nЦена: 25 RUB/Месяц\nДля приобретения прав пожалуйста напишите /dev_info"



logging.basicConfig(level=logging.INFO)



# Initialize bot and dispatcher

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



@dp.message_handler(commands=['start', 'help'])

async def send_welcome(message: types.Message):

    admin_id = message.from_user.id

    if admin_id not in admin_ids and admin_id != owner_id:

        await message.reply(message_for_guest)

        return

    await message.reply("Напишите запрос для получения ответа, вы также можете сменить модель, для смены напишите /switch")

    if admin_id == owner_id:

        await asyncio.sleep(1)

        await bot.send_message(admin_id,

            f"Вы владелец, для вас доступны следующие команды:\n/view_admins - посмотреть действующих админов бота (те, кто может им пользоваться)\n/add_admin - добавить нового администратора (он сможет пользоваться ботом). Например, используйте /add_admin 2, чтобы добавить администратора с id 2\n/remove_admin - удалить администратора. Пример: /remove_admin 2, где мы удаляем администратора с id 2\nВаш ID: {owner_id}")

# Обработчик команды /switch
@dp.message_handler(Command("switch"))
async def switch_models(message: types.Message):
    admin_id = message.from_user.id

    if admin_id not in admin_ids and admin_id != owner_id:

        await message.reply(message_for_guest)

        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    models = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-instant-100k",
        "claude-instant",
        "claude+",
        "gpt-4-poe",
        "gpt-3.5-turbo-poe",
        "Sage"
    ]
    for model in models:
        keyboard.add(InlineKeyboardButton(model, callback_data=model))
    await message.reply("Выбери модель:", reply_markup=keyboard)


# Обработчик выбора модели
@dp.callback_query_handler(lambda c: c.data in [
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-instant-100k",
    "claude-instant",
    "claude+",
    "gpt-4-poe",
    "gpt-3.5-turbo-poe",
    "Sage"
])
async def choose_model(callback_query: types.CallbackQuery, state: FSMContext):
    global model
    model = callback_query.data
    await state.update_data(model=model)
    await bot.answer_callback_query(callback_query.id, f"Ты выбрал модель: {model}")
    await callback_query.message.edit_reply_markup(reply_markup=None)

# Просмотр списка admin_ids

@dp.message_handler(commands=("view_admins"))

async def view_admins(message: types.Message):

    if message.from_user.id == owner_id:

        admins_list = "\n".join(str(admin_id) for admin_id in admin_ids)

        await message.reply(f"Список admin_ids:\n{admins_list}")

    else:

        await message.reply('Данная команда не доступна. ')



# Удаление admin_id из списка

@dp.message_handler(commands=("remove_admin"))

async def remove_admin(message: types.Message):

    if message.from_user.id == owner_id:

        # Получаем аргумент - admin_id для удаления

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

    admin_id = message.from_user.id

    if message.from_user.id != owner_id:

        await message.reply("Данная команда не доступна. ")

        return



    # Получаем ID пользователя, которого нужно добавить в качестве администратора

    if len(message.text.split()) > 1:

        new_admin_id = int(message.text.split()[1])

        if new_admin_id not in admin_ids:

            admin_ids.append(new_admin_id)

            await message.reply("Администратор успешно добавлен.")

        else:

            await message.reply("Этот пользователь уже является администратором.")

    else:

        await message.reply("Укажите ID пользователя, которого нужно добавить.")



@dp.message_handler(Command('image'))
async def cmd_image(message: types.Message):
    admin_id = message.from_user.id

    if admin_id not in admin_ids and admin_id != owner_id:

        await message.reply(message_for_guest)

        return
    # отправляем сообщение пользователю с запросом на ввод текста для промпта
    await message.answer("Введите текст для промпта:")
    # переводим бота в состояние ожидания текста от пользователя
    await ImagePrompt.waiting_for_text.set()

@dp.message_handler(state=ImagePrompt.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    try:
        await bot.send_message(message.from_user.id,"Обработка успешна началась, ожидайте 🕓")
        prompt_text = message.text
        response = openai.Image.create(
            prompt=prompt_text,
            n=2,
            size="1024x1024"
        )
        for image in response['data']:
            await bot.send_photo(message.chat.id, photo=image['url'])
        await state.finish()
    except openai.error.APIError as e:
        error_message = "Произошла ошибка при создании изображения: "
        if hasattr(e, 'response') and 'detail' in e.response:
            error_message += e.response['detail']
        else:
            error_message += str(e)
        await message.answer(error_message)

@dp.message_handler(commands=['dev_info'])

async def send_dev_info(message: types.Message):

    from_u = message.from_user

    user_id, first_name, username, language_code, is_premium = from_u.id, from_u.first_name, from_u.username, from_u.language_code, from_u.is_premium



    await message.reply(f"Ваш ID: {user_id}\nДля покупки прав обратитесь к @trainee_developer и сообщите ваш ID")

    await bot.send_message(owner_id, f"Новое сообщение по команде /dev_info:\n➖➖➖➖➖➖➖➖➖➖➖➖\nUser ID: {user_id}\nFirst Name: {first_name}\nUsername: @{username}\nLanguage Code: {language_code}\nTelegram Premium: {is_premium}\n➖➖➖➖➖➖➖➖➖➖➖➖")




@dp.message_handler()

async def response_all(message: types.Message):

    admin_id = message.from_user.id

    if admin_id not in admin_ids and admin_id != owner_id:

        await message.reply(message_for_guest)

        return

    message_text = ''

    if message.chat.type == "private":

        message_text = message.text

        await message.reply("Обработка запроса, ожидайте!")

        response = await bing_chat(message_text)
        await bot.send_message(admin_id,f"Ответ от {model}:\n{response}")

async def bing_chat(message_text):
  response = openai.ChatCompletion.create(
    model=model,
    messages=[
        {'role': 'user', 'content': message_text},
    ],
    max_tokens=120
  )
  content = response['choices'][0]['message']['content']
  return content



if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)
