FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./run_telegram_bot.py ./
COPY ./config.json ./config.json

CMD [ "python", "./run_telegram_bot.py" ]