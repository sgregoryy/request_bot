from loader import dp
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart, Command
from states.states import *
from keyboards.inline import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import uuid
import threading
import time
import asyncio
from loader import bot



async def try_delete_call(call: types.CallbackQuery):
    try:
        await call.message.delete()
    except:
        pass

async def try_edit_call(callback, text, markup):
    try:
        msg = await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=markup)
    except:
        await try_delete_call(callback)
        msg = await callback.message.answer(text=text, parse_mode='HTML', reply_markup=markup)
    return msg

async def try_edit_call_photo(callback, text, markup, id):
    try:
        msg = await callback.message.edit_text(text=text, parse_mode='HTML', reply_markup=markup)
    except:
        await try_delete_call(callback)
        msg = await callback.message.answer_photo(caption=text, photo=id, parse_mode='HTML', reply_markup=markup)
    return msg

ADMIN_ID = 761232572
def save_value(value, filename='wallet.txt'):
    with open(filename, 'w') as file:
        file.write(str(value))

# Загрузка значения из файла
def load_value(filename='wallet.txt'):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None
wallet_addres = load_value()
# Определяем область доступа
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

    # Открываем таблицу по ключу
sheet = client.open_by_key('1otbEtPjlvq6lA4c_53JJb7WeQZne8Jg794UN4c1m5po').sheet1

@dp.message(F.text == '/admin')
async def handle_admin(message: types.Message):
    # await message.a
    if int(message.from_user.id) == ADMIN_ID:
        await message.answer('Админ панель', reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Изменить кошелек', callback_data='change_wallet')]
            ]
        ))

@dp.callback_query(F.data == 'change_wallet')
async def handle_change_wallet(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f'Введите новый адрес кошелька(текущий - {wallet_addres}): ')
    await state.set_state(AdminWallet.wallet)
    await call.answer()


@dp.message(AdminWallet.wallet)
async def handle_new_wallet(message: types.Message, state: FSMContext):
    await state.update_data({ 'wallet': message.text })
    save_value(value=message.text)
    await message.answer(f'Адрес успешно изменен на {message.text}')
    await state.clear()

@dp.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print('start command data',data)
    if data:
        print('start command data',data)
        table = sheet.get_all_records()
        for i, row in enumerate(table):
            if row.get('ID') == data['uuid'] and not row.get('status'):  # Если строка найдена и статус не установлен
                row_number = i + 2
                sheet.delete_rows(row_number)
                print(f"Строка с UUID {data['uuid']} удалена из-за тайм-аута.")
                await state.clear()
    await message.answer('Hi bro, in this bot you can leave a request to create a token, you need to fill in the information (There is also a small fee of 0.03 sol for token transfers)', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Make request', callback_data='start_req')]
        ]
    ), message_effect_id='5046509860389126442')
    
@dp.message(Command('start'))
async def handle_start(message: types.Message, state: FSMContext):
    # data = await state.get_data()
    data = await state.get_data()
    print('start command data',data)
    if data:
        print('start command data',data)
        table = sheet.get_all_records()
        for i, row in enumerate(table):
            if row.get('ID') == data['uuid'] and not row.get('status'):  # Если строка найдена и статус не установлен
                row_number = i + 2
                sheet.delete_rows(row_number)
                print(f"Строка с UUID {data['uuid']} удалена из-за тайм-аута.")
                await state.clear()
    await message.answer('Hi bro, in this bot you can leave a request to create a token, you need to fill in the information (token creation fee 6.5 million tokens)', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Make request', callback_data='start_req')]
        ]
    ), message_effect_id='5046509860389126442')    

@dp.callback_query(F.data == 'start_req')
async def handle_start_req(call: types.CallbackQuery, state: FSMContext):
    await try_edit_call(call, text='Pick the date you want', markup=date_keyboard())
    await state.set_state(Application.date)
    # await call.message.answer(text='Pick the date you want', reply_markup=date_keyboard())
    await call.answer()

@dp.message(Command('new_request'))
async def handle_new_req(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data:
        print(data)
        table = sheet.get_all_records()
        for i, row in enumerate(table):
            if row.get('ID') == data['uuid'] and not row.get('status'):  # Если строка найдена и статус не установлен
                row_number = i + 2
                sheet.delete_rows(row_number)
                print(f"Строка с UUID {data['uuid']} удалена из-за тайм-аута.")
                await state.clear()
    await message.answer(text='Pick the date you want', reply_markup=date_keyboard())
    await state.set_state(Application.date)
    # await call.message.answer(text='Pick the date you want', reply_markup=date_keyboard())
    # await call.answer()

@dp.callback_query(Application.date)
async def handle_date(call: types.CallbackQuery, state:FSMContext):
    date = call.data.split('_')[1]
    times = get_free_time(date)
    print('handler')
    print(times)
    if len(times) < 1:
        await try_edit_call(callback=call, text=f'There is no free time on {date}.', markup=date_keyboard())
        # await call.message.answer(f'There is no free time on {date}.', reply_markup=date_keyboard())
    else:    
        await state.update_data({ 'date': date })
        await try_edit_call(callback=call, text='Choose a free time (in UTC timezone)', markup=time_keyboard(date, times))
        # await call.message.answer('Choose a free time ', reply_markup=time_keyboard(date, times))
        await state.set_state(Application.ticker)
        print(await state.get_data())
    await call.answer()

async def start_timer(uuid, timeout, user_id, state: FSMContext):
    await asyncio.sleep(timeout)  # Ждем указанное время
    
    # Поиск и удаление строки, если заявка не завершена
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get('ID') == uuid and not row.get('Hash transaction'):  # Если строка найдена и статус не установлен
            row_number = i + 2
            sheet.delete_rows(row_number)
            print(f"Строка с UUID {uuid} удалена из-за тайм-аута.")
            await bot.send_message(user_id, 'Your request is out of time')
            await state.clear()
            return

@dp.callback_query(F.data.contains('time_'))
async def handle_time(call: types.CallbackQuery, state: FSMContext):
    time = call.data.split('_')[1]
    await state.update_data({'time': time})

    # Генерация UUID
    uuid_str = str(uuid.uuid4())
    await state.update_data({'uuid': uuid_str})

    # Запись даты и времени в таблицу
    data = await state.get_data()
    row = [
        uuid_str,
        data.get('date'),
        data.get('time'),
        "", "", "", "", "", "", "", "", "", "", ""  # Пустые поля, которые будут заполнены позже
    ]
    sheet.append_row(row)

    # Запуск таймера для удаления записи
    asyncio.create_task(start_timer(uuid_str, 1800, call.from_user.id, state))

    await call.message.answer('Write the ticker (For example: DOGE): ')
    await state.set_state(Application.ticker)
    await call.answer()

@dp.message(F.text, Application.ticker)
async def handle_ticker(message: types.Message, state: FSMContext):
    await state.update_data({ 'ticker': message.text })
    await state.set_state(Application.desc)
    await message.answer('''Write a description
Important: In the description at the beginning it will say "prod by https://t.me/bad_ass_dev, dev tokens frozen": ''')

@dp.message(F.text, Application.desc)
async def handle_desc(message: types.Message, state: FSMContext):
    await state.update_data({ 'desc': message.text })
    await state.set_state(Application.image)
    await message.answer('Send an image for your token: ')

@dp.message(F.photo, Application.image)
async def handle_image(message: types.Message, state: FSMContext):
    if message.photo[0]:
        await state.update_data({ 'image': message.photo[0].file_id })
        await state.set_state(Application.twit_link)
        await message.answer('Do you need to specify Twitter (X), if not, send "-"')
    else:
        await message.answer('Send image!')
        await state.set_state(Application.image)

@dp.message(F.text, Application.twit_link)
async def handle_tw_link(message: types.Message, state: FSMContext):
    await state.update_data({ 'twit_link': message.text })
    await state.set_state(Application.tg_link)
    await message.answer('Do you need to specify Telegram, if no, send "-"')

@dp.message(F.text, Application.tg_link)
async def handle_tg_link(message: types.Message, state: FSMContext):
    await state.update_data({ 'tg_link': message.text })
    await state.set_state(Application.website_link)
    await message.answer('Do you need to specify a website, if no, send "-"')

@dp.message(F.text, Application.website_link)
async def handle_website_link(message: types.Message, state: FSMContext):
    await state.update_data( { 'website_link': message.text } )
    await state.set_state(Application.wallet)
    await message.answer('Enter the address of the wallet from which the sol will be sent')

@dp.message(F.text, Application.wallet)
async def handle_wallet(message: types.Message, state: FSMContext):
    await state.update_data({ 'wallet': message.text })
    await state.set_state(Application.sol_amount)
    await message.answer('Enter the number of sols (minimum 3 sol, maximum 7 sol). \nFor example: 3.4, 5, 6.7')

@dp.message(F.text, Application.sol_amount)
async def handle_sol(message: types.Message, state: FSMContext):
    sol_amount = float(message.text)
    # wallet_addres = 'asf'
    if sol_amount > 7 or sol_amount < 3:
        await message.answer('Wrong number of sol.')
        await state.set_state(Application.sol_amount)
    else:
        await state.update_data({ 'sol_amount': sol_amount })
        await state.set_state(Application.transaction_hash)
        await message.answer(f'Send sol to this address: <code>{wallet_addres}</code>  and send a hash of the transaction (you can find it on solscan) ', parse_mode='HTML')

@dp.message(F.text, Application.transaction_hash)
async def handle_hash(message: types.Message, state: FSMContext):
    await state.update_data({'transaction_hash': message.text, 'tg_teg': '@' + message.from_user.username})
    data = await state.get_data()
    uuid_str = data.get('uuid')

    # Обновление строки в таблице
    row_number = find_row_by_uuid(uuid_str)
    if row_number:
        sheet.update(f'D{row_number}:N{row_number}', [
            [
             data.get('ticker'),
             data.get('desc'),
             data.get('image'),
             data.get('twit_link'),
             data.get('tg_link'),
             data.get('website_link'),
             data.get('wallet'),
             data.get('sol_amount'),
             data.get('transaction_hash'),
             data.get('status'),
             data.get('tg_teg')]
        ])

    await state.clear()
    await state.set_state(User.user_id)
    await state.update_data({'user_id': message.from_user.id, 'uuid': uuid_str})
    await message.answer('Please wait for the confirmation of your request.')
    await bot.send_photo(
        ADMIN_ID,
        photo=data['image'],
        caption=f'''Дата: {data['date']}\nВремя: {data['time']}\nТикер: {data["ticker"]}\nКошелек: {data['wallet']}\nКол-во sol: {data['sol_amount']}\nХеш: <code>{data['transaction_hash']}</code>\nID: <code>{uuid_str}</code>''',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Подтвердить', callback_data='confirm_true'),
                 InlineKeyboardButton(text='Отклонить', callback_data='confirm_false')]
            ]
        ),
        parse_mode='HTML'
    )
@dp.callback_query(F.data.contains('confirm_'))
async def handle_confirm(call: types.CallbackQuery, state: FSMContext):
    flag = call.data.split('_')[1]
    data = await state.get_data()
    if flag == 'true':
        print(call.message)
        await try_edit_call_photo(call, call.message.caption + '\n <b>Подтверждено</b>✅', None, call.message.photo[0].file_id)
        await bot.send_message(chat_id=data['user_id'], text='Your request has been confirmed!')
        await state.clear()
        find_and_update_row(data['uuid'], '✓')
        await call.answer()
    else:
        await try_edit_call_photo(call, call.message.caption + '\n <b>Отклонено</b> ❌', None, call.message.photo[0].file_id)
        await bot.send_message(chat_id=data['user_id'], text='Your request has been rejected')
        await state.clear()
        find_and_delete_row(data['uuid'])
        await call.answer()

# def find_and_delete_row(uuid)

def find_and_delete_row(uuid):
    # worksheet = sh.sheet1  # Или укажите нужный лист

    # Получаем все записи из таблицы
    data = sheet.get_all_records()

    # Поиск строки с указанным UUID
    for i, row in enumerate(data):
        if row.get('ID') == uuid:  # Предполагаем, что столбец с UUID называется 'ID'
            # Удаление строки (i+2, так как `get_all_records` возвращает только данные, а не заголовок)
            sheet.delete_rows(i + 2)
            print(f"Строка с UUID {uuid} удалена.")
            return

    print(f"Строка с UUID {uuid} не найдена.")
def find_and_update_row(uuid, symbol):
    # Получаем все строки таблицы
    data = sheet.get_all_records()

    # Ищем строку с нужным UUID
    for i, row in enumerate(data):
        if row.get('ID') == uuid:  # Замените 'uuid' на имя колонки, где хранятся UUID
            # Обновляем ячейку в найденной строке
            row_number = i + 2  # Нумерация строк в gspread начинается с 1, а первая строка содержит заголовки
            sheet.update_cell(row_number, 13, symbol)  # Обновляем ячейку в 3-м столбце (индексация начинается с 1)
            print(f"Обновлена строка {row_number}")
            return
    
    print("UUID не найден")

async def save_to_google_sheets(data):
    # Открываем Google Sheets
    

    # Получаем данные из state
    # data = await state.get_data()

    # Генерируем уникальный ID для записи
    user_id = str(uuid.uuid4())  # Это создаст уникальный UUID. Можно использовать другой метод генерации ID.

    # Формируем строку для записи
    row = [
        user_id,
        data.get('date'),
        data.get('time'),
        data.get('ticker'),
        data.get('desc'),
        data.get('image'),
        data.get('twit_link'),
        data.get('tg_link'),
        data.get('website_link'),
        data.get('wallet'),
        data.get('sol_amount'),
        data.get('transaction_hash'),
        data.get('status'),
        data.get('tg_teg')
    ]

    # Записываем строку в таблицу
    sheet.append_row(row)

    # Очистка state после записи
    # await state.clear()
    return user_id


# Пример вызова функции
# В вашем обработчике вызовите эту функцию после завершения диалога с пользователем
def find_row_by_uuid(uuid):
    data = sheet.get_all_records()
    for i, row in enumerate(data):
        if row.get('ID') == uuid:
            return i + 2  # Нумерация строк в gspread начинается с 1
    return None
