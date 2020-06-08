# Сервис для просмотра древовидной структуры данных в PostgresSQL

Тестовая задача

    1. Создать модель таблицы в PostgresSQL
        - id UUIDField
        - parеnt_id ForeignKey(self.id)
        - title CharField(256)
        - registered_in DateTimeField(auto_add_now=True)
    2. Заполнить модель тестовыми данными
        - глубина заполнения 5 уровней
        - к каждому узлу подключено 5 элементов
    3. Реализовать на SQLAlchemy функцию, которая
        - принимает параметр sort_fld, поле для сортировки
        - принимает параметр sort_dir (asc/dsc), направление сортировки
        - принимеет параметр depth (глубина выборки) и выводит требуемое кол-во уровней
            - т.е. при depth=1 дожны вернуться прямые потомки узла
        - при вызове без указания стартового узла, стартовым узлом считается корень
        - при вызове от с указанием узла, стартуем от него
    4. Написать тест (pytest) для проверки работоспособности функции
    5. Реализовать всё асинхронно



### Демонстрация

Для запуска демонстрации должны быть установлены docker, docker-compose.

Клонируем репозиторий

```
YOUR_REPOS_DIR=<YOUR_REPOS_DIR>
cd $YOUR_REPOS_DIR
git clone git@github.com:ve-i-uj/tree-viewer.git
PROJECT_DIR=$YOUR_REPOS_DIR/tree-viewer
```

Копируем нужные переменные окружения (конфигурацию) в корень проекта (создаём файл .env в корне проекта).

```
cd $PROJECT_DIR
bash script/update_env.sh dev
```

Собираем и запускаем проект


```
docker-compose build
docker-compose up
```

Через SwaggerAPI можно взаимодействовать с приложением.
[Swagger API](http://127.0.0.1:8080/)  



### Локальная разработка

Создаём виртуальное окружение

```
PROJECT_DIR=<YOUR_PROJECT_DIR>
cd PROJECT_DIR
mkdir .pyvenv
python3.7 -m venv .pyvenv
source .pyvenv/bin/activate
```

Копируем нужную конфигурацию

```
cd $PROJECT_DIR
cp data/docker.dev.env .env
```

Разрабатываем.
