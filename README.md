# Foodgram

![Foodgram Workflow Status](https://github.com/rasputin-pro/foodgram-project-react/actions/workflows/workflow.yml/badge.svg?branch=master&event=push)
___
![Python](https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?logo=django&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
---

Это учебный проект **«Продуктовый помощник»** на базе фреймворка Django.
К проекту подключён фронтэнд — React

На этом сервисе пользователи могут публиковать рецепты, 
подписываться на публикации других пользователей, добавлять 
понравившиеся рецепты в список «Избранное», а перед походом 
в магазин скачивать сводный список продуктов, необходимых для 
приготовления одного или нескольких выбранных блюд.


## Стек технологий:
- Python 3.7
- Django 2.2.28
- PostgreSQL
- Docker
- Nqinx


## Как запустить проект:

>Для запуска проекта на компьютере должен быть установлен **docker compose**

Клонируйте репозиторий:
```
git@github.com:rasputin-pro/foodgram-project-react.git
```

В папке `infra_local` создайте файл `.env` с переменными для работы с базой 
данных:
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # Придумайте сложный пароль
DB_HOST=db # название контейнера, оставьте как есть
DB_PORT=5432
```

В коммандной строке перейдите в папку `infra_local`, и разверните проект в 
docker compose:
```commandline
docker compose up -d
```

Загрузите демонстрационные данные в базу данных:
```commandline
docker compose exec -it backend python manage.py loaddata dump.json
```
> В демонстрационных данных нет изображений!
> Для авторизации можно воспользоваться учётной записью:
> 
> Имя пользователя: `review`
>
> Пароль: `PaSSWoRD111`
>
> Email: `review@mail.ru`
> 
> Сайт — [http://localhost](http://localhost)
> Админка — [http://localhost/admin](http://localhost/admin).


## Документация API
После запуска программы документация будет доступна по адресу:

[http://localhost/api/docs/](http://localhost/api/docs/)
