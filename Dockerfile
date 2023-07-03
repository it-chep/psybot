FROM python:3.9

# Установка Redis-сервера
RUN apt-get update && apt-get install -y redis-server

# Определение переменной окружения для порта Redis-сервера
ENV REDIS_PORT=6379

# копирование кода Django-приложения и установка зависимостей
WORKDIR .
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Удаление ошибки "Connection reset by peer" при использовании Redis-сервера
RUN sed -i '1258,1266d' "/usr/local/lib/python3.9/site-packages/redis/connection.py"
# Установка необходимых инструментов для отладки
RUN apt-get update && apt-get install -y redis-tools nano net-tools

# Запуск Redis-сервера и Django runserver
CMD redis-server --port $REDIS_PORT & python manage.py runserver 0.0.0.0:8000

