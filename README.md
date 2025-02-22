# Mega Test Project

Данные суперпользователя:

username: admin
password: admin

## Описание

Mega Test - это тестовое задание. Проект включает в себя функциональность CRUD, а также работу с Celery для отправки уведомлений.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/marlenovtilek/Mega_test.git
   cd Mega_test
Создайте виртуальное окружение и активируйте его:

python -m venv venv
source venv/bin/activate  # Для Windows используйте venv\Scripts\activate

Установите зависимости:
pip install -r requirements.txt
Выполните миграции:

python manage.py migrate
Запустите сервер:

python manage.py runserver
Запуск с помощью Docker
Если вы используете Docker, выполните следующие шаги:

### Запуск с помощью Docker

Если вы используете Docker, выполните следующие шаги:

1. Соберите и запустите контейнер:

   ```bash
   docker-compose up -d --build


Функциональность
Регистрация и аутентификация пользователей
CRUD операции для книг и авторов
Добавление и удаление книг из избранного
Уведомления о новых книгах и юбилейных изданиях с помощью Celery


### Тестирование
Для запуска тестов используйте следующую команду:
python manage.py test


Используемые технологии
Django
Django REST Framework
SQLite3
Celery
HTML/CSS для фронтенда
Копировать
Редактировать


