from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

positions = ('Python Web', 'Data Analyst', 'QA', 'Java', 'JavaScript')

position_keyboard = ReplyKeyboardMarkup()
position_keyboard.add(KeyboardButton('Python Web'), KeyboardButton('Data Analyst'),
                      KeyboardButton('QA'), KeyboardButton('Java'),
                      KeyboardButton('JavaScript'))
