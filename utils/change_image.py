import re
from io import BytesIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from aiogram.types import InputFile


def add_text_to_image(image_path='./media/1.jpg', vacancy_name: str = None, company_name: str = None,
                      salary: str = None) -> InputFile:
    """
add_text_to_image(image_path='./media/1.jpg', vacancy_name: str = None, company_name: str = None,
salary: str = None) -> InputFile
This function opens an image, adds text to it, saves it and returns the modified image as InputFile object.
The function takes in 3 optional parameters:
- image_path: The filepath of the image to be modified, default is './media/1.jpg'
- vacancy_name: name of the vacancy, the text to be added to the image.
- company_name: name of the company, the text to be added to the image.
- salary: salary of the vacancy, the text to be added to the image.

The function uses the python Imaging Library (PIL) to open the image and draw on it.
It uses 3 different fonts to write the texts on the image, './media/vacancy_font.ttf', './media/company_font.ttf' and './media/salary_font.ttf'
The text is written on the specified positions on the image (80, 130), (80, 230) and (80, 850) respectively for vacancy_name, company_name and salary.
The modified image is then saved in './media/saved_images/' directory with the name of the image as save_name.
The modified image is then read as binary and returned as InputFile object.
Returns:
InputFile: The binary content of the modified image wrapped as a InputFile object.
"""

    image = Image.open(image_path)

    draw = ImageDraw.Draw(image)

    save_name = vacancy_name.split(' ')[0:2]
    save_name = " ".join(save_name) + '-' + company_name
    save_name = re.sub(r'/', '', save_name)
    save_name = re.sub(r',', '', save_name)

    vacancy_font = ImageFont.truetype(font='./media/vacancy_font.ttf', size=80)
    company_font = ImageFont.truetype(font='./media/company_font.ttf', size=80)
    salary_font = ImageFont.truetype(font='./media/company_font.ttf', size=50)

    draw.text(xy=(80, 130), text=vacancy_name, font=vacancy_font, fill=(0, 0, 0))
    draw.text(xy=(80, 230), text=company_name, font=company_font, fill=(0, 0, 0))
    draw.text(xy=(80, 850), text=salary, font=salary_font, fill=(0, 0, 0))

    image.save(f'./media/saved_images/{save_name}.jpg')

    with open(f'./media/saved_images/{save_name}.jpg', 'rb') as file:
        photo = InputFile(BytesIO(file.read()), "image.jpg")

    return photo
