import os

from aiogram import Bot, Dispatcher, executor, types

import exceptions
import expenses
from categories import Categories
from middlewares import AccessMiddleware

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
ACCESS_ID = os.getenv('TELEGRAM_ACCESS_ID')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Sends welcome message and bot help"""
    await message.answer(
        'Considering finance bot\n\n'
        'Add an expense: 250 taxi\n'
        'Today statistic: /month\n'
        'Last added expenses: /expenses\n'
        'Expenses categories: /categories'
    )


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Deletes an entry about expense by its id"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = 'Deleted'
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Sends expenses categories list"""
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " + \
        ("\n* ".join([c.name + ' (' + ", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Sends today expenses statistic"""
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    """Sends current month expenses statistic"""
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Sends a few last expenses entries"""
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer('No expenses yet')
        return

    last_expenses_rows = [
        f'{expense.amount} rub on {expense.category_name} - press '
        f'/del{expense.id} for deleting'
        for expense in last_expenses
    ]
    answer_message = 'The last saved expenses:\n\n ' + \
        '\n\n* '.join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Adds a new expense"""
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f'Added expenses {expense.amount} rub on {expense.category_name}.\n\n'
        f'{expenses.get_today_statistics()}'
    )
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
