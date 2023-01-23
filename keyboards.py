import json
from pprint import pprint

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

positions = ('Python Web', 'Data Analyst', 'QA', 'Java', 'JavaScript')

position_keyboard = ReplyKeyboardMarkup()
position_keyboard.add(KeyboardButton('Python Web'), KeyboardButton('Data Analyst'),
                      KeyboardButton('QA'), KeyboardButton('Java'),
                      KeyboardButton('JavaScript'))


def areas():
    with open('vacancies_json/states.json') as file:
        cities = json.load(file)
    return cities


def get_state_keyboard():
    states = areas()
    states_keyboard = ReplyKeyboardMarkup()
    for state in states:
        states_keyboard.add(KeyboardButton(state['state']))
    return states_keyboard


def get_states_list():
    states_list = []
    states = areas()
    for state in states:
        states_list.append(state['state'])
    return states_list


def get_cities_keyboard(state_name):
    states = areas()
    cities_keyboard = ReplyKeyboardMarkup()
    for state in states:
        if state['state'] == state_name:
            for city in state['cities']:
                cities_keyboard.add(KeyboardButton(city['name']))
    return cities_keyboard



def get_cities_list(state_name):
    cities_list = []
    states = areas()
    for state in states['areas']:
        if state['name'] == state_name:
            for city in state['areas']:
                cities_list.append(city['name'])
    return cities_list


def get_all_cities():
    all_cities = []
    states = areas()
    for state in states:
            for city in state['cities']:
                all_cities.append(city['name'])
    return all_cities


all_cities = get_all_cities()
states_list = get_states_list()

