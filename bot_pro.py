from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import logging
from base import DatabaseManager
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import asyncio

from config import API_TOKEN_PRO, SUPER_PRO, class_names, special_class_names, MED_PEOPLES

logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    wait_class = State()
    wait_full_name = State()
    details = State()
    wait_details = State()


bot = Bot(token=API_TOKEN_PRO)
dp = Dispatcher()

database_manager = DatabaseManager("Users")

admin_only = lambda message: message.from_user.id not in SUPER_PRO

button_spisok = KeyboardButton(text="Список учеников")
button_add_leave = KeyboardButton(text="Отметить отсутствующих")
back = KeyboardButton(text="Отмена")
keyboard_main = ReplyKeyboardMarkup(keyboard=[[button_spisok, button_add_leave]], resize_keyboard=True)
keyboard_back = ReplyKeyboardMarkup(keyboard=[[back]], resize_keyboard=True)


@dp.message(admin_only)
async def handle_unwanted_users(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    return


@dp.message(F.text.startswith('Отмена'))
async def spisok_teachers(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Отмена...", reply_markup=keyboard_main)

@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    await message.reply(
        "Вы можете посмотреть в данном боте список учеников или отметить тех, кто заболел или уезжает по заявлению",
        reply_markup=keyboard_main)


@dp.message(F.text.startswith('Список учеников'))
async def spisok_teachers(message: types.Message, state: FSMContext):
    await message.reply('Введите номер и букву класса в формате: 11a  (буква с маленькой буквы и без пробелов).\n'
                        'Либо введите просто "10" или "11" или "все", чтобы увидеть все 10, 11 или и 10, и 11 классы',
                        reply_markup=keyboard_back)
    await state.set_state(Form.wait_class)


@dp.message(Form.wait_class)
async def return_users(message: types.Message, state: FSMContext):
    if message.text in class_names:
        await message.reply("```" + database_manager.get_info_class(message.text) + "```", parse_mode = "MarkdownV2")
        await message.reply("Если вы хотите узнать более детальную информацию об ученике, введит его фамилию и имя в "
                            "формате 'Иванов Иван'. Если нет, то нажмите копку отмена", reply_markup=keyboard_back)
        await state.set_state(Form.wait_details)

    elif message.text in special_class_names:
        for s in database_manager.get_info_special(message.text):
            await message.reply("```" + s + "```", reply_markup=keyboard_back, parse_mode = "MarkdownV2")
        await message.reply("Если вы хотите узнать более детальную информацию об ученике, введит его фамилию и имя в "
                            "формате 'Иванов Иван'. Если нет, то нажмите копку отмена", reply_markup=keyboard_back)
        await state.set_state(Form.wait_details)
    else:
        await message.reply('Такого класса не существует, попробуйте ещё раз')


@dp.message(Form.wait_details)
async def get_user_details(message: types.Message, state: FSMContext):
    l = message.text.split()
    if len(l) == 2:
        name = " ".join(message.text.split()[:2])
        if database_manager.name_in_base(name):
            await message.reply(database_manager.get_info_name(name),  reply_markup=keyboard_main)
            await message.reply(
                "Если вы хотите узнать более детальную информацию о другом ученике, введите его фамилию и имя в "
                "формате 'Иванов Иван'. Если нет, то нажмите копку отмена", reply_markup=keyboard_back)
        else:
            await message.reply('Неправильное введеное имя (и/или фамилия)')
    else:
        await message.reply('Неккоректные данные или  формат данных')


@dp.message(F.text.startswith('Отметить отсутствующих'))
async def chekname(message: types.Message, state: FSMContext):
    await message.reply('Введите имя и фамилию обучающегося в формате:\n"Иванов Иван б" - если болеет\n"Иванов Иван з" - '
                        'если отсутствует по заявлению\n"Иванов Иван т" - если ученик вернулся в цод.\n\nЕсли вы '
                        'нажали случайно, отмените заявку', reply_markup=keyboard_back)
    await state.set_state(Form.wait_full_name)


@dp.message(Form.wait_full_name)
async def get_user(message: types.Message):
    l = message.text.split()
    if len(l) == 3 and (l[2] == "б" or l[2] == "з" or l[2] == "т"):
        name = " ".join(message.text.split()[:2])
        if database_manager.name_in_base(name):
            database_manager.set_out(name, l[2])
            await message.reply('Статус успешно установлен. Отметьте ещё одного ученика или нажмите отмена для выхода')
        else:
            await message.reply('Неправильное введеное имя (и/или фамилия)')
    else:
        await message.reply('Неккоректные данные')

@dp.message()
async def spisok_teachers(message: types.Message):
    await message.reply("Я не понял :(", reply_markup=keyboard_main)


async def main_pro():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main_pro())
