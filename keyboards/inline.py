from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
from datetime import timedelta
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# import uuid

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

    # Открываем таблицу по ключу
sheet = client.open_by_key('1otbEtPjlvq6lA4c_53JJb7WeQZne8Jg794UN4c1m5po').sheet1

def date_keyboard():
    today = datetime.datetime.today()
    timezone = pytz.timezone('UTC')
    timezoned_datetime = timezone.localize(today)
    timezoned_date = timezoned_datetime.date()
    markup = InlineKeyboardMarkup(inline_keyboard=[])
    for i in range(0, 3):
        markup.inline_keyboard.append([InlineKeyboardButton(text=f'{timezoned_date + datetime.timedelta(days=i)}', callback_data=f'date_{timezoned_date + datetime.timedelta(days=i)}')])
    return markup

def get_free_time(date_str):
    rows = sheet.get_all_records()
    timezone = pytz.timezone('UTC')
    date = timezone.localize(datetime.datetime.strptime(date_str, '%Y-%m-%d'))
    current_time = datetime.datetime.now(timezone)
    print(current_time)
    # current_time = timezone.localize(current_time)
    times  = ['13:00', '14:00', '15:00', '16:00', '16:30', '17:00', '17:30']
    # print(rows)
    records_by_date = []
    for row in rows:
        # print(row['date'], date_str)
        if row['date'] == date_str:
            # print(1)
            if row['Time'] in times:
                times.remove(row['Time'])
    print(date.date())
    if date.date() == current_time.date():
        print(1)
        times = [time for time in times if timezone.localize(datetime.datetime.strptime(time, '%H:%M').replace(year=date.year, month=date.month, day=date.day)) > current_time + timedelta(hours=1)]
    # print(current_time.date())
    print(times)
    return times

def time_keyboard(date_str, times):
    # times = ['15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00']
    current_time = datetime.datetime.now()
    timezone = pytz.timezone('UTC')
    current_time = timezone.localize(current_time)
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    # Если дата не сегодня, возвращаем весь список
    # if date.date() != current_time.date():
    #     # for 
    #     available_times = times
    # else:
    #     # Фильтруем времена, которые больше текущего времени
    #     available_times = [time for time in times if timezone.localize(datetime.datetime.strptime(time, '%H:%M').replace(year=date.year, month=date.month, day=date.day)) > current_time + timedelta(hours=1)]

    # Создаем инлайн-клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    print(times)
    for time in times:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=time, callback_data=f"time_{time}")])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text='🔙', callback_data='start_req')])
    return keyboard

# get_free_time('2024-08-15')