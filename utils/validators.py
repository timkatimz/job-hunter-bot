import re


def validate_description_requirements(description: str, requirements: str) -> tuple[str, str]:
    """
validate_description_requirements(description: str, requirements: str) -> tuple[str, str]
This function takes in two strings, job description and job requirements and applies some modifications to them.
It replaces <highlighttext> with empty string, * with empty string.
If the description is None then the function replace the description with 'Отсутствует'
If the requirements is None then the function replace the requirements with 'Отсутствуют'
Returns:
tuple[str, str]: Tuple of two strings, one representing the modified job description and other representing the modified job requirements.
"""
    if description is None:
        description = 'Отсутствует'
    else:
        description = re.sub(r'<highlighttext>', '', description)
        description = re.sub(r'</highlighttext>', '', description)
        description = re.sub(r'\*', '', description)
    if requirements is None:
        requirements = 'Отсутствуют'
    else:
        requirements = re.sub(r'<highlighttext>', '', requirements)
        requirements = re.sub(r'</highlighttext>', '', requirements)
        requirements = re.sub(r'\*', '', requirements)

    return description, requirements


def validate_salary(salary: dict) -> str:
    """
validate_salary(salary: dict) -> str
This function takes in a dictionary representing salary and returns a string representing the salary.
It first checks if the salary dictionary is not None.
Then it extracts the values from the salary dictionary such as 'from', 'to' and 'currency' and 
format them into a string.
It replaces 'RUR' with 'рублей'.
If the salary dictionary is None, then it returns 'Не указана'
Returns:
str: A string representing the salary.
"""
    if salary:
        salary_text = f''
        currency = salary['currency']
        currency = re.sub(r'RUR', 'рублей', currency)
        if salary['from']:
            salary_text = f"от {salary['from']} "
        if salary['to']:
            salary_text += f"до {salary['to']} "
        salary_text += f'{currency}'
    else:
        salary_text = 'Не указана'
    return salary_text
