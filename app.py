import asyncio
import logging
import os
import re
from typing import List, Dict, Any, Iterable

from aiogram import Bot, types, exceptions
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from keyboards import positions, position_keyboard, get_state_keyboard, get_cities_keyboard, states_list, all_cities
from models.models import User
from setup_db import db
from start_app import start_app
from utils.utils import create_user, write_vacancies, send_one_vacancy, send_logs, get_db_file
from utils.utils import first_vacancies, open_vacancies, get_vacancies, delete_files_from_folder

app = start_app(db)
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(filename='./logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')




@dp.message_handler(commands='start')
async def cmd_start(msg: types.Message):
    """
    This function is a message handler for the command "start" in the Telegram bot.
    
    When the command is received, the function checks if the user who sent the message 
    is already registered in the database. If the user is already registered, the bot 
    sends a message saying "You are already registered." 
    Otherwise, the function logs that the user has started the registration process 
    and sends a message asking the user to select a position, with a reply keyboard for
    choosing the position.
    """
    user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
    if user:
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Вы уже зарегистрированы', reply_markup=markup)
    else:
        logging.info(f"{msg.chat.full_name} начал регистрацию")
        await bot.send_message(msg.chat.id, 'Выберите позицию:', reply_markup=position_keyboard)
        

@dp.message_handler(commands='help')
async def get_help(msg: types.Message):
    help_text = f'Работа бота заключается в персональном подборе вакансий для пользователя на сайте HeadHunter.\nВакансии подбираются'
    help_text += f' на основе указанных пользователем данных:\n\n- Позиция (Python, QA, Java и т.д)\n'
    help_text += f'- Локация (Выбор локации доступен в меню). После выбора локации, пользователь будет получать вакансии только по выбранному городу\n\n'
    help_text += f'Выбор позиции является обязательным условием для получения вакансий. Выбор локации на усмотрение пользователя.'
    help_text += f'\nЕсли локация не выбрана, пользователь будет получать новые вакансии доступные на территории РФ\n'
    help_text += f'Выбор градации невозможен. По умолчанию, градация всех позиций - "Junior"\n\n'
    help_text += f'Пользователю доступен выбор только одной позиции и одной локации с выбором конкретного города.\n'
    help_text += f'Для смены позиции нужно отписаться (Меню -> Отписаться от рассылки) и подписаться заново '
    help_text += f'(Меню -> Подписатсья на рассылку) с выбором другой позиции.\nДля смены локации достаточно выбрать в меню пункт "Выбор локации" и выбрать новую из списка.\n'
    help_text += f'Чтобы убрать привязку к локации: Меню -> "Удалить привязку к локации" \n\n'    
    help_text += f'Если у вас возникнут дополнительные вопросы, можно задать их @s_tee'
    await bot.send_message(msg.chat.id, help_text)
    
    
@dp.message_handler(commands='commands')
async def get_commands(msg: types.Message):
    command_text = '<strong>Список доступных команд</strong>:\n\n'
    command_text += '/start - команда для начала работы с ботом и регистрации пользователя\n'
    command_text += '/unsubscribe - команда для отписки от рассылки вакансий\n'
    command_text += '/set_location - команда для выбора или смены локации\n'
    command_text += '/remove_location - команда для сброса данных о локации\n'
    command_text += '/help - команда для предоставлении дополнительной информации о боте'
    await bot.send_message(msg.chat.id, command_text, parse_mode=types.ParseMode.HTML)
    


@dp.message_handler(commands='set_location')
async def set_location(msg: types.Message):
    user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
    if user:
        states_keyboard = get_state_keyboard()
        await bot.send_message(msg.chat.id, "Выберите область из списка", reply_markup=states_keyboard)
    else:
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Для выбора локации, нужно подписаться', reply_markup=markup)
    
@dp.message_handler(lambda msg: msg.text in states_list)
async def set_city(msg: types.Message):
    user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
    if user:
        if msg.text in ['Москва', 'Санкт-Петербург']:
            user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
            user.city = msg.text
            db.session.commit()
            markup: any = types.ReplyKeyboardRemove(True)
            await bot.send_message(msg.chat.id, 'Запомнил. Теперь я буду присылать только вакансии, доступные в вашем городе', reply_markup=markup)
        else:
            cities_keyboard = get_cities_keyboard(msg.text)
            await bot.send_message(msg.chat.id, 'Выберите город из списка', reply_markup=cities_keyboard)
    else:
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Сначала нужно подписаться', reply_markup=markup)
        


@dp.message_handler(lambda msg: msg.text in all_cities)
async def set_user_city(msg: types.Message):
    user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
    if user:
        user.city = msg.text
        db.session.commit()
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Запомнил. Теперь я буду присылать только вакансии, доступные в вашем городе', reply_markup=markup)
    else:
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Сначала нужно подписаться', reply_markup=markup)



@dp.message_handler(commands='remove_location')
async def remove_location(msg: types.Message):
    user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
    user.city = None
    db.session.add(user)
    db.session.commit()
    await bot.send_message(msg.chat.id, 'Запомнил. Теперь я буду отправлять вам вакансии без привязки к локации')


@dp.message_handler(commands='db')
async def cmd_get_db(msg: types.Message):
    """
    This function is a message handler for the Telegram bot using the dp object. 
    
    It handles the command 'db' and performs the following actions:
        - Queries the database for a user with the username 's_tee' and assigns the result to the variable tim.
        - Retrieves the database file using the get_db_file() function.
        - Sends the retrieved database file as a document to the chat associated with the user 's_tee'.
    """
    tim = db.session.query(User).filter(User.username == 's_tee').first()
    db_file = get_db_file()
    await bot.send_document(tim.chat_id, document=db_file)


@dp.message_handler(commands='unsubscribe')
async def cmd_unsubscribe(msg: types.Message):
    """
    This function is a message handler for the command "unsubscribe" in the Telegram bot.

    When the command is received, the function checks if the user who sent the message is 
    already subscribed in the database by checking the user's username. If the user is 
    already subscribed, the function removes the user from the database and sends a message
    saying "Hope you unsubscribed because you've got the job ^_^", and logs that the user 
    has unsubscribed. Otherwise, the function sends a message saying "You are not subscribed 
    to the mailing list. To subscribe, use the /start command."
    """
    user = db.session.query(User).filter(User.username == msg.chat.username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        logging.info(f"{msg.chat.full_name}  Отписался")
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Надеемся, Вы отписались потому-что получили оффер ^_^', reply_markup=markup)
    else:
        markup: any = types.ReplyKeyboardRemove(True)
        await bot.send_message(msg.chat.id, 'Вы не подписаны на рассылку.\nДля подписки используйте команду /start', reply_markup=markup)


@dp.message_handler(commands='all_users')
async def cmd_all_users(msg: types.Message):
    """
    This function is a message handler for the command "all_users" in the Telegram bot.
    
    When the command is received, the function retrieves all the users from the database
    and counts the number of users. Then, it creates a string containing information about 
    each user, including their username and position. Then, it sends the message with the 
    user information to the user with username 's_tee' chat_id.
    """
    users = db.session.query(User).all()
    tim = db.session.query(User).filter(User.username == 's_tee').first()
    user_info = f'Всего пользователей - {len(users)}\n'
    for user in users:
        user_info += f'@{user.username} - {user.position} - {user.city}\n'
    await bot.send_message(tim.chat_id, user_info)


@dp.message_handler(commands='logs')
async def cmd_send_logs(msg: types.Message):
    """
    This function is a message handler for the command "logs" in the Telegram bot. 
    
    When the command is received, the function retrieves the user object with the 
    username 's_tee' from the database, then call send_logs() function which probably 
    retrieves the logs from a file or database, and sends the logs as a message to 
    the user's chat_id.
    """
    tim = db.session.query(User).filter(User.username == 's_tee').first()
    logs = send_logs()
    await bot.send_message(tim.chat_id, logs)


    
    
@dp.message_handler(lambda msg: msg.text in positions, content_types=types.message.ContentTypes.TEXT)
async def set_position(msg: types.Message):
    """
    This function is a message handler for text messages in the Telegram bot. 
    When a text message is received, the function first checks if the user who sent 
    the message is already registered in the database by checking their user_id. If 
    the message text matches with any of the predefined positions, it removes the reply 
    keyboard and check if user is already registered if yes it sends a message saying 
    "You are already registered" else it creates a new user with the data 
    (user_id, chat_id, username, position) and calls open_vacancies and first_vacancies 
    functions to get the first available job opening for the chosen position and sends 
    the message containing the job opening information to the user. If the message text 
    doesn't match any predefined position, it sends a message saying "I don't know that command".
    """

    user = db.session.query(User).filter(User.user_id == msg.from_user.id).first()
    
    position_name: str = msg.text.lower()
    position_name: str = re.sub(r' ', '_', position_name)
    markup: any = types.ReplyKeyboardRemove(True)
    if user:
        await bot.send_message(msg.chat.id, 'Вы уже зарегистрированы', reply_markup=markup)
    else:
        create_user(user_id=msg.from_user.id, chat_id=msg.chat.id, username=msg.chat.username,
                    position=position_name)
        vacancies: List[Dict[str, Any]] = open_vacancies(position_name)
        text: str = first_vacancies(vacancies)
        logging.info(f"{msg.chat.full_name} закончил регистрацию")
        await bot.send_message(msg.chat.id, text, reply_markup=markup, parse_mode=types.ParseMode.HTML)


@dp.message_handler(content_types=types.message.ContentTypes.ANY)
async def del_flood_msg(msg: types.Message):
    """
    This function is a message handler for any type of messages in the Telegram bot. 
    When any message received, this function will delete the received message immediately. 
    It could be use as an anti-flood mechanism.
    """
    await msg.delete()
    


async def vacancy_for_user():
    """
    This function is used to send new job openings to users who are subscribed to a 
    specific position. It first retrieves all the users from the database and logs the
    total number of users. Then, it loops through a predefined list of positions. For 
    each position, it calls the get_vacancies() function to retrieve new job openings 
    and the open_vacancies() function to retrieve old job openings. Then, it compares
    the new and old job openings, and sends new job openings to users who are subscribed 
    to that specific position.

    It also checks if the user is blocked by the bot, if yes it deletes the user from 
    the database and logs the action.

    It also calls delete_files_from_folder() function to delete files from the folder
    and calls write_vacancies(new_vacancies, position) to write new vacancies to file
    """

    users: Iterable = db.session.query(User).all()
    logging.info(f'Запустился.\nВсего пользователей - {len(users)}')
    positions_name: tuple = ('python_web', 'data_analyst', 'qa', 'java', 'javascript')
    for position in positions_name:
        logging.info(f'Перебираю позиции {position.capitalize()}')
        new_vacancies: List[Dict[str, Any]] = get_vacancies(position)
        old_vacancies: List[Dict[str, Any]] = open_vacancies(position)
        for new_vacancy in new_vacancies:
            if new_vacancy in old_vacancies:
                continue
            else:
                logging.info(f"Нашел вакансию:\n{new_vacancy['name']}")
                if users:
                    for user in users:
                        if user.city is None:
                            if user.position == position:
                                logging.info('Нашел подходящего юзера без города')
                                vacancy_text, markup, photo = send_one_vacancy(new_vacancy)
                                try:
                                    await bot.send_photo(user.chat_id, photo, caption=vacancy_text, reply_markup=markup,
                                                        parse_mode=types.ParseMode.HTML)

                                except exceptions.BotBlocked:
                                    db.session.delete(user)
                                    db.session.commit()
                                    logging.info(f'Пользователь удален')
                                    continue
                            else:
                                continue
                        else:
                            if user.position == position and user.city == new_vacancy['location']:
                                logging.info('Нашел подходящего юзера с городом')
                                vacancy_text, markup, photo = send_one_vacancy(new_vacancy)
                                try:
                                    await bot.send_photo(user.chat_id, photo, caption=vacancy_text, reply_markup=markup,
                                                        parse_mode=types.ParseMode.HTML)

                                except exceptions.BotBlocked:
                                    db.session.delete(user)
                                    db.session.commit()
                                    logging.info(f'Пользователь удален')
                                    continue
                            else:
                                continue
                else:
                    continue
        delete_files_from_folder()
        write_vacancies(new_vacancies, position)
        logging.info(f'Перезаписал вакансии {position}')


async def send_me_logs():
    """
    This function is an asynchronous function called "send_me_logs". It performs 
    the following actions:

     - Queries the "User" table in the "db" session for a user with the username "s_tee" 
        and assigns the result to the variable "tim".
     - Calls another function "send_logs" and assigns the returned value to a variable "logs".
     - Sends a message to the chat ID of the user found in step 1 with the logs obtained 
        in step 2, and the parse mode is set to "types.ParseMode.HTML".
        
    """
    tim = db.session.query(User).filter(User.username == 's_tee').first()
    logs = send_logs()
    await bot.send_message(tim.chat_id, logs, parse_mode=types.ParseMode.HTML)


async def repeat_my_function():
    """ 
    This function is an asynchronous function called "repeat_my_function".
    It is an infinite loop that performs the following actions:
        - Calls an asynchronous function "vacancy_for_user" and waits for it to complete.
        - Calls an asynchronous function "send_me_logs" and waits for it to complete.
        - Pauses the loop for 3600 seconds (1 hour) using the "asyncio.sleep" function.

    This loop will continue indefinitely, repeatedly calling the "vacancy_for_user" and 
        "send_me_logs" functions and pausing for 1 hour between each iteration.
    """

    while True:
        await vacancy_for_user()
        await send_me_logs()
        await asyncio.sleep(3600)  # задержка 1 час


if __name__ == '__main__':
    #loop = asyncio.get_event_loop()
    #loop.create_task(repeat_my_function())
    executor.start_polling(dp)
