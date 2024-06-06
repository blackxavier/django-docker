
###########
# BUILDER 1 #
###########
# pull official base image
FROM krallin/ubuntu-tini:trusty as tini
# pull official base image
FROM python:3.11.4-slim-buster as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

# install python dependencies
RUN pip install --upgrade pip
COPY . /usr/src/app/
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt



#########
# FINAL #
#########

# pull official base image
FROM python:3.11.4-slim-buster

# Copy tini package
COPY --from=tini /usr/local/bin/tini /usr/local/bin/tini

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint.prod.sh
COPY ./app-entrypoint.prod.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/app-entrypoint.sh
RUN chmod +x  $APP_HOME/app-entrypoint.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.prod.sh with tini
ENTRYPOINT ["/usr/local/bin/tini", "--", "/home/app/web/app-entrypoint.sh"]




