FROM python:3.9-slim

ARG PORT

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT

CMD ['python','webui_playground.py'] 