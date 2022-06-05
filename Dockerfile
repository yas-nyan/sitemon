FROM python:3.7-bullseye

RUN apt-get update && apt-get -y install fping
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install pipenv
COPY Pipfile /app/
COPY Pipfile.lock /app/

RUN pipenv install

COPY lib /app/lib
COPY sitemon.py /app/

CMD ["pipenv","run","sitemon"]