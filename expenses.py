import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
    """New expense message structure"""
    amount: int
    category_text: str


class Expense(NamedTuple):
    """New expense structure which was added to DB"""
    id: Optional[int]
    amount: int
    category_name: str


def add_expense(raw_message: str) -> Expense:
    """Adds a new message"""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(parsed_message.category_text)
    inserted_row_id = db.insert('expense', {
        'amount': parsed_message.amount,
        'created': _get_now_formatted(),
        'category_codename': category.codename,
        'raw_text': raw_message
    })

    return Expense(
        id=None,
        amount=parsed_message.amount,
        category_name=category.name
    )


def get_today_statistics() -> str:
    """Returns today expenses"""
    cursor = db.get_cursor()
    cursor.execute(
        'SELECT sum(amount) FROM expense WHERE date(created)=date("now", "localtime")'
    )
    result = cursor.fetchone()
    if not result[0]:
        return 'No expenses today yet'
    all_today_expenses = result[0]
    cursor.execute(
        'SELECT sum(amount) FROM expense WHERE date(created)=date("now", "localtime") AND category_codename IN (SELECT codename FROM category WHERE is_base_expense=true)'
    )
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0

    return (
        f'Today expenses: \n'
        f'total - {all_today_expenses} rub\n'
        f'base - {base_today_expenses} rub from {_get_budget_limit} rub \n\n'
    )


def get_month_statistics() -> str:
    """Returns current month expenses"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(
        f'SELECT sum(amount) FROM expense WHERE date(created) >= "{first_day_of_month}"'
    )
    result = cursor.fetchone()
    if not result[0]:
        return 'No expenses this month yet'

    all_today_expenses = result[0]
    cursor.execute(
        f'SELECT sum(amount) FROM expense WHERE date(created) >= "{first_day_of_month}" AND category_codename IN (SELECT codename FROM category WHERE is_base_expense=true)'
    )
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (
        f'Current month expenses:\n'
        f'total - {all_today_expenses} rub \n'
        f'base - {base_today_expenses} rub from {now.day * _get_budget_limit()} rub'
    )


def last() -> List[Expense]:
    """Returns a few last expenses"""
    cursor = db.get_cursor()
    cursor.execute(
        'SELECT e.id, e.amount, c.name FROM expense e LEFT JOIN category c ON c.codename=e.category_codename ORDER BY created DESC LIMIT 10'
    )
    rows = cursor.fetchall()
    last_expenses = [Expense(
        id=row[0],
        amount=row[1],
        category_name=row[2]
    ) for row in rows]

    return last_expenses


def delete_expense(row_id: int) -> None:
    """Deletes message by its id"""
    db.delete('expense', row_id)


def _parse_message(raw_message: str) -> Message:
    """Parse text of the coming message about a new expense"""
    regexp_result = re.match(r'([\d]+) (.*)', raw_message)
    if not regexp_result or not regexp_result.group(0) or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Can't understand the message. Write the message in the format, for instance: \n1500 a subway"
        )
    amount = regexp_result.group(1).replace(' ', '')
    category_text = regexp_result.group(2).strip().lower()
    return Message(
        amount=amount,
        category_text=category_text
    )


def _get_now_formatted() -> str:
    """Returns today date by sring"""
    return _get_now_datetime().strftime('%Y-%m-%d %H:%M:%S')


def _get_now_datetime() -> datetime.datetime:
    """Returns today datetime with time zone Moscow"""
    tz = pytz.timezone('Europe/Moscow')
    return datetime.datetime.now(tz)


def _get_budget_limit() -> int:
    """Returns a daily limit of expenses for basic base expenses"""
    return db.fetch_all('budget', ['daily_limit'])[0]['daily_limit']
