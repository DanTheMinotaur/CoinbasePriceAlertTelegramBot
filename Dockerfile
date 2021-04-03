FROM python:3.7

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./
COPY cryptoprices/ ./cryptoprices/
COPY price_alert.py ./

RUN pip install pipenv

RUN pipenv install --deploy --system

CMD [ "python", "./price_alert.py" ]