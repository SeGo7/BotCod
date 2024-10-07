from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import logging
from base import DatabaseManager
from config import API_TOKEN_CHILD
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from datetime import datetime

import asyncio

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN_CHILD)
dp = Dispatcher()

database_manager = DatabaseManager("Users")


class Form(StatesGroup):
    wait_name = State()


@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message, state: FSMContext):
    if database_manager.id_in_base(message.from_user.id):
        await message.reply("Вы уже зарегистрированы, можете продолжать пользоваться ботом!")
    else:
        await message.reply("Привет! Это бот для записи на прогулки. Введи свое фамилие и имя в формате (Иванов Иван)")
        await state.set_state(Form.wait_name)


@dp.message(Form.wait_name)
async def handle_message(message: types.Message, state: FSMContext):
    if database_manager.registration_child(message.text, message.from_user.id):
        button_go_walk = KeyboardButton(text="Записаться на прогулку")
        button_end_walk = KeyboardButton(text="Вернуться с прогулки")
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_go_walk, button_end_walk]], resize_keyboard=True)
        await message.reply("Поздравляем, вы успешно зарегистрированы."
                            "Пожалуйста, отправьте ваш номер телефона в формате (+79999999999) Чтобы дополнить информацию о вас."
                            "Если же вы не хотите, то можете начинать пользоваться ботом прямо сейчас. Далее в любое время "
                            "для добавления вашего телефона в базу, просто введите его в формате выше.",
                            reply_markup=keyboard)
        await state.clear()

    else:
        await message.reply(
            "Фамилия и имя введены не правильно. Введите их по образцу (Иванов Иван).\nБукву ё не заменяйте на е.")


@dp.message(F.text.startswith('Записаться на прогулку'))
async def go_on_walk(message: types.Message):
    if not database_manager.is_walk(message.from_user.id):
        if 0 <= datetime.now().hour < 24:
            res = database_manager.set_walk_true(message.from_user.id)
            if res:
                await message.reply("Вы успешно записаны и должны вернуться до " + res)
            else:
                await message.reply("Вас не удалось записать, видимо возникла непредведенная ошибка")

        else:
            await message.reply(
                "Вы не можете выйти на прогулку до 15:00 и после 17:00 без заявления, обратитесь к воспитателю")
    else:
        await message.reply("Вы уже на прогулке")


@dp.message(F.text.startswith('Вернуться с прогулки'))
async def back_from_walk(message: types.Message):
    if database_manager.is_walk(message.from_user.id):
        if database_manager.return_from_walk(message.from_user.id):
            if 15 <= datetime.now().hour < 17:
                await message.reply(("Ваша прогулка завершена вовремя, поздравляем!"))
            else:
                await message.reply("Вы опоздали!")
        else:
            await message.reply("Произошла неизвестная ошибка")
    else:
        await message.reply("Вы не на прогулке")


@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if database_manager.registration_child(message.text, message.from_user.id):
        button_go_walk = KeyboardButton(text="Записаться на прогулку")
        button_end_walk = KeyboardButton(text="Вернуться с прогулки")
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_go_walk, button_end_walk]], resize_keyboard=True)
        await message.reply("Поздравляем, вы успешно зарегистрированы."
                            "Пожалуйста, отправьте ваш номер телефона в формате (+79999999999) Чтобы дополнить информацию о вас."
                            "Если же вы не хотите, то можете начинать пользоваться ботом прямо сейчас. Далее в любое время "
                            "для добавления вашего телефона в базу, просто введите его в формате выше.",
                            reply_markup=keyboard)
    elif database_manager.add_phone_number(message.from_user.id, message.text):
        await message.reply("Телефон добавлен")
    else:
        await message.reply("Ваше сообщение не корректно. Введите данные в правильном формате.")


async def main_child():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запуск асинхронного цикла событий
    asyncio.run(main_child())
