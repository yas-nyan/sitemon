FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get -y install fping curl dnsutils

WORKDIR /app
RUN pip install poetry
COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN poetry config virtualenvs.create false \
  && poetry install

COPY sitemon.py /app/

CMD ["python3","sitemon.py"]