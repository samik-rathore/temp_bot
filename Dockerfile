FROM python:3.11

WORKDIR /app

COPY requirements.text /app/

RUN pip3 install -r requirements.txt

COPY . /app

CMD python3 main.py