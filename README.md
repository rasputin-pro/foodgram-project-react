# Foodgram

![Yamdb Workflow Status](https://github.com/rasputin-pro/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master&event=push)
___


Это учебный проект **«Продуктовый помощник»**. 
На этом сервисе пользователи смогут публиковать рецепты, 
подписываться на публикации других пользователей, добавлять 
понравившиеся рецепты в список «Избранное», а перед походом 
в магазин скачивать сводный список продуктов, необходимых для 
приготовления одного или нескольких выбранных блюд.

## Как запустить проект:

>Для запуска проекта на сервере должен быть установлен docker compose

Клонируйте репозиторий:
```
git@github.com:rasputin-pro/foodgram-project-react.git
```

В коммандной строке перейдите в папку `infra`, и разверните проект в docker 
compose:
```commandline
docker compose up -d
```

Создайте суперпользователя:
```commandline
docker compose exec backend python manage.py createsuperuser
```



## Документация
После запуска проекта - по адресу: `http://localhost/api/docs/` доступна 
документация.
