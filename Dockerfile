FROM python:3.10.7

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install vim \
    && apt-get -y install python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /srv/docker-server
ADD . /srv/docker-server
WORKDIR /srv/docker-server
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

ARG SECRET_KEY
ENV SECRET_KEY=$SECRET_KEY

# ARG POSTGRES_NAME
# ARG POSTGRES_USER
# ARG POSTGRES_PASSWORD
# ARG POSTGRES_HOST
# ARG POSTGRES_PORT
ARG CF_ID
ARG CF_TOKEN

ENV CF_ID=$CF_ID
ENV CF_TOKEN=$CF_TOKEN
# ENV POSTGRES_NAME=$POSTGRES_NAME
# ENV POSTGRES_USER=$POSTGRES_USER
# ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
# ENV POSTGRES_HOST=$POSTGRES_HOST
# ENV POSTGRES_PORT=$POSTGRES_PORT

COPY poetry.lock pyproject.toml /srv/docker-server/
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# RUN python manage.py makemigrations
# RUN python manage.py migrate

# EXPOSE 8000
# CMD ["python", "manage.py", "runserver","0:8000"]
