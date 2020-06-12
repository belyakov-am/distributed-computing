FROM python:3.7

# set work directory
WORKDIR /usr/src/backend

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
COPY ./Pipfile /usr/src/backend/Pipfile
COPY ./Pipfile.lock /usr/src/backend/Pipfile.lock
RUN pipenv install --system

# copy entrypoint.sh
COPY ./bin/entrypoint.sh /entrypoint.sh

# copy project
COPY . /usr/src/backend/

# tmp
# run entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["app:start"]
