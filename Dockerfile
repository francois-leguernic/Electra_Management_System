FROM python:3.13-slim

ARG POETRY_VERSION=1.8.1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY ./src /app/src
COPY ./tests /app/tests
COPY station_config.json /app/
COPY main.py /app/


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]