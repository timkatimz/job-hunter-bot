FROM python:3.10-slim

# set work directory
WORKDIR /code

# install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

RUN flask db migrate
RUN flask db upgrade
# run flask
CMD ["python", "app.py"]
