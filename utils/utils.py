import json
import os
import re
from io import BytesIO
from typing import Union, BinaryIO, List, Dict, Any

import requests
from aiogram import types

from models.models import User
from setup_db import db
from utils.change_image import add_text_to_image
from utils.validators import validate_description_requirements, validate_salary


def get_vacancies(position_name: str) -> List[Dict[str, Any]]:
    """

    This function takes in a single argument, position_name which is a string representing 
    the name of the position for which you want to fetch the vacancies.
    
    It reads urls from the file './vacancies_json/api_urls.json' and filters 
    the url that corresponds to the position_name passed as an argument.
    
    Then it calls vacancies_for_new_users function with the filtered url and 
    returns the list of vacancies
    
    """
    with open('./vacancies_json/api_urls.json', 'r') as f:
        urls = json.load(f)
    for url in urls:
        if position_name == url['name']:
            vacancies = vacancies_for_new_users(url['url'])
    return vacancies


def vacancies_for_new_users(position_url: str) -> List[Dict[str, Any]]:
    """

    This function takes in a single argument, position_url which is a string 
    representing the url of the position for which you want to fetch the vacancies.
    
    It fetches the vacancies data from the API using requests library.
    
    It iterates through the API response and filters the vacancies with experience of 3-6 years.
    
    Then it extracts the required data of each vacancy like name, salary, schedule, 
    created_at, published_at, experience, company, location, description, requirements,
    skills, url
    
    It calls validate_description_requirements and validate_salary function to format 
    the description, requirements and salary respectively.
    
    It replaces dashes in location with underscores.
    
    Finally, it returns the list of vacancies in form of dictionary
    """

    vacancies = []
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'HH-User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64)'}

    with requests.get(position_url, headers=headers) as api_vacancies:
        api_vacancies = api_vacancies.json()

        for url in api_vacancies['items']:
            with requests.get(url['url'], headers=headers) as response:
                full_vacancy = response.json()
            if full_vacancy['experience']['id'] != 'between3And6':

                vacancy_name = full_vacancy['name']
                salary = full_vacancy['salary']
                schedule = full_vacancy['schedule']['name']
                created_at = full_vacancy['created_at']
                published_at = full_vacancy['published_at']
                experience = full_vacancy['experience']['name']
                company = full_vacancy['employer']['name']
                location = full_vacancy['area']['name']
                description = url['snippet']['responsibility']
                requirements = url['snippet']['requirement']
                description, requirements = validate_description_requirements(description, requirements)
                url = full_vacancy['alternate_url']
                skills = [skill['name'] for skill in full_vacancy['key_skills']]

                if skills is None:
                    skills = 'Не указаны'
                else:
                    skills = ", ".join(skills)

                if experience == 'Нет опыта':
                    experience = re.sub(r'Нет опыта', 'Можно без опыта', experience)
                salary = validate_salary(salary)

                location = re.sub(r'-', '_', location)

                vacancies.append({
                    'name': vacancy_name,
                    'salary': salary,
                    'company': company,
                    'created_at': created_at,
                    'published_at': published_at,
                    'schedule': schedule,
                    'experience': experience,
                    'location': location,
                    'description': description,
                    'requirements': requirements,
                    'skills': skills,
                    'url': url
                })
            else:
                continue

    return vacancies


def write_vacancies(vacancies: List[Dict[str, Any]], position_name: str) -> None:
    """
This function writes a list of vacancies to a JSON file.

Args:
vacancies (List[Dict[str, Any]]): A list of dictionaries containing information about the vacancies.
position_name (str): The name of the position for which the vacancies are being written.

Returns:
None

"""
    with open(f'./vacancies_json/{position_name}.json', 'w') as f:
        json.dump(vacancies, f, indent=2, ensure_ascii=False, sort_keys=True)


def open_vacancies(position_name: str) -> List[Dict[str, Any]]:
    """
This function opens a JSON file containing a list of vacancies and returns the data in the form of a list of dictionaries.

Args:
position_name (str): The name of the position for which the vacancies are being read.

Returns:
List[Dict[str, Any]]: A list of dictionaries containing information about the vacancies.

"""
    with open(f'./vacancies_json/{position_name}.json', 'r', encoding='utf-8') as f:
        vacancies = json.load(f)
    return vacancies


def first_vacancies(vacancies: List[Dict[str, Any]]) -> str:
    """
This function takes a list of dictionaries containing information about vacancies and returns a string containing the name, experience, salary, location, requirements and url of the first five vacancies.

Args:
vacancies (List[Dict[str, Any]]): A list of dictionaries containing information about the vacancies.

Returns:
str: A string containing the name, experience, salary, location, requirements and url of the first five vacancies.

"""
    first_vacancy = 'Как только появится новая вакансия, я вам сообщу.\nА пока можете просмотреть подборку новых вакансий на вашу позицию:\n\n'
    for vacancy in vacancies[0:5]:
        first_vacancy += f"<strong>{vacancy['name']}</strong>\n"
        first_vacancy += f"<strong>Опыт:</strong> {vacancy['experience']}. <strong>з/п:</strong> {vacancy['salary']}\n"
        first_vacancy += f"<strong>Локация:</strong>  #{vacancy['location']}\n"
        first_vacancy += f"<strong>Требования:</strong>\n{vacancy['requirements']}\n"
        first_vacancy += f"<a href=\'{vacancy['url']}\'>Подробнее</a>\n\n"
    return first_vacancy


def create_user(user_id, chat_id, username, position) -> None:
    """
This function creates a new user and adds it to the database.

Args:
user_id (int): The user's unique identifier.
chat_id (int): The chat's unique identifier.
username (str): The user's username.
position (str): The user's position.

Returns:
None
"""
    user = User(user_id=user_id, chat_id=chat_id, username=username, position=position)
    db.session.add(user)
    db.session.commit()


def send_one_vacancy(vacancy: dict) -> Union[str, any, BinaryIO]:
    """
This function creates a string, an InlineKeyboardMarkup object, and a photo from 
the given vacancy's information.

Args:
vacancy (dict): A dictionary containing information about a single vacancy, including 
the name, schedule, company, location, salary, experience, description, requirements, skills, and url.

Returns:
Union[str, any, BinaryIO]: A string containing information about the vacancy, 
an InlineKeyboardMarkup object with a button to apply to the vacancy, and a photo
with the vacancy's information.
"""
    vacancy_text = f"<strong>Позиция:</strong> {vacancy['name']}\n" \
                   f"#{vacancy['schedule'].replace(' ', '_').lower()}\n\n" \
                   f"<strong>Компания:</strong> {vacancy['company']}\n" \
                   f"<strong>Локация:</strong> #{vacancy['location']}\n" \
                   f"<strong>Зарплата:</strong> {vacancy['salary']}\n" \
                   f"<strong>Опыт:</strong> {vacancy['experience']}\n\n" \
                   f"<strong>Краткое описание:</strong>\n {vacancy['description']}\n\n" \
                   f"<strong>Требования:</strong> \n{vacancy['requirements']}\n\n" \
                   f"<strong>Ключевые навыки:</strong> {vacancy['skills']}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Откликнуться', url=vacancy['url']))
    photo = add_text_to_image(vacancy_name=vacancy['name'],
                              company_name=vacancy['company'],
                              salary=vacancy['salary'])
    return vacancy_text, markup, photo


def delete_created_image(save_name: str) -> None:
    """
delete_created_image(save_name: str) -> None:
This function deletes the image with the specified name from the 'media/saved_images' directory.
The image should have a '.jpg' extension.
Args:
save_name (str): The name of the image file to be deleted.
Returns:
None
"""
    if os.path.exists(save_name):
        os.remove(f'./media/saved_images/{save_name}.jpg')


def delete_files_from_folder():
    """
delete_files_from_folder() -> None
This function deletes all files from the 'media/saved_images' directory.
Returns:
None
"""
    for file in os.listdir('./media/saved_images'):
        file_path = os.path.join('./media/saved_images', file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')


def send_logs() -> str:
    """
send_logs() -> str
This function reads the last 20 lines of the 'logs.txt' file and returns the logs as a string.
Returns:
str: The last 20 lines of logs from the 'logs.txt' file.
    """
    log = ''
    with open('./logs.txt', 'r') as f:
        logs = f.readlines()
    for string in logs[-20:-1]:
        log += string
    return log


def get_db_file() -> types.InputFile:
    """
    get_db_file() -> types.InputFile
This function opens the 'instance/database.db' file and reads it as binary. 
It then returns it as a InputFile object.

Returns:
types.InputFile: The binary content of 'instance/database.db' file wrapped as a InputFile object.
    """
    with open('./instance/database.db', 'rb') as file:
        db_file = types.InputFile(BytesIO(file.read()), filename='database.db')
    return db_file
