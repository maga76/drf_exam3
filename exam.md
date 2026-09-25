# EXAM PROJECT REPORT

## 1. Общая информация

Проект — backend интернет-магазина компьютерной техники на Django.

Текущая структура специально сделана просто:

```text
exam_week3/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── exam.md
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── myapp/
    ├── migrations/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    └── views.py
```

В проекте одно Django-приложение: `myapp`.

---

## 2. Что уже написано

### Django project

- [x] Создан Django project `core`.
- [x] Создано приложение `myapp`.
- [x] `myapp` добавлено в `INSTALLED_APPS`.
- [x] Используется SQLite.
- [x] Настроены `MEDIA_URL` и `MEDIA_ROOT`.
- [x] Часовой пояс: `Asia/Dushanbe`.
- [x] Настроен `AUTH_USER_MODEL = "myapp.CustomUser"`.
- [x] Команда `python manage.py check` прходит без ошибок.

### CustomUser

Модель наследуется от `AbstractUser`.

Добавлены поля:

- [x] `phone`;
- [x] `role`;
- [x] `avatar`.

Роли:

- `user`;
- `manager`;
- `admin`.

### Category

Добавлены:

- [x] название;
- [x] описание;
- [x] изображение;
- [x] `__str__`.

### Product

Основные поля:

- [x] категория;
- [x] название;
- [x] бренд;
- [x] тип товара;
- [x] описание;
- [x] цена;
- [x] количество на складе;
- [x] изображение.

Типы товаров:

- laptop;
- desktop PC;
- CPU;
- GPU;
- motherboard;
- RAM;
- storage;
- PSU;
- case;
- cooling;
- monitor;
- other.

Упрощённые характеристики хранятся прямо в `Product`:

- [x] CPU;
- [x] GPU;
- [x] socket;
- [x] тип RAM;
- [x] объём RAM;
- [x] объём хранилища;
- [x] мощность блока питания;
- [x] требуемая мощность GPU;
- [x] оценка экрана;
- [x] оценка батареи;
- [x] оценка производительности;
- [x] игровая оценка.

### Review

- [x] Связь с пользователем.
- [x] Связь с товаром.
- [x] Оценка.
- [x] Текст отзыва.
- [x] Дата создания.

### Wishlist

- [x] Хранит пользователя.
- [x] Хранит добавленный товар.

### CompareItem

- [x] Хранит пользователя.
- [x] Хранит товар для сравнения.
- [x] Позволяет в будущем сравнить несколько товаров.

### Cart и CartItem

- [x] `Cart` хранит корзину пользователя.
- [x] `CartItem` хранит товар и его количество.

### Order и OrderItem

`Order` хранит:

- [x] пользователя;
- [x] статус;
- [x] имя и фамилию;
- [x] телефон;
- [x] город;
- [x] адрес;
- [x] общую сумму;
- [x] дату создания.

`OrderItem` хранит:

- [x] заказ;
- [x] товар;
- [x] цену;
- [x] количество.

### PCBuild

Модель сохраняет сборку ПК:

- [x] пользователь;
- [x] название сборки;
- [x] CPU;
- [x] GPU;
- [x] motherboard;
- [x] RAM;
- [x] storage;
- [x] PSU;
- [x] case;
- [x] итоговая цена.

---

## 3. Что специально упрощено

Чтобы код соответствовал пройденному уровню, сейчас не используются:

- validators;
- `Meta` в моделях;
- `UniqueConstraint`;
- `unique_together`;
- `OneToOneField`;
- `ManyToManyField`;
- отдельные specification-модели;
- signals;
- managers;
- service layer;
- repository pattern;
- Docker, PostgreSQL, Redis, Celery;
- frontend и 3D-визуализация.

---

## 4. Что ещё НЕ написано

### Database

- [x] Создана migration `myapp/migrations/0001_initial.py` для текущего `models.py`.
- [x] Текущие модели применены к новой `db.sqlite3`.
- [ ] Тестовые данные не созданы.

Старая несовместимая база сохранена локально в `db_before_new_migrations.sqlite3`. Она не отправляется в GitHub.

### Django Admin

- [x] Все текущие модели зарегистрированы в `admin.py`.
- [ ] Superuser не создан в текущей версии базы.

### API

- [x] Django REST Framework подключён в `INSTALLED_APPS`.
- [x] Создан `serializers.py`.
- [x] Для текущих моделей написаны простые `ModelSerializer`.
- [x] Для текущих моделей написаны простые `ModelViewSet`.
- [x] Принято решение не использовать `router`.
- [x] API URLs написаны вручную через `path()` и `as_view()`.
- [x] Базовые CRUD endpoints подключены.
- [x] Добавлены поиск, простые фильтры, ordering и pagination товаров.

### Authentication

- [x] Register endpoint написан.
- [x] Login endpoint написан.
- [x] JWT authentication настроена.
- [x] Access/refresh tokens подключены.
- [x] Logout и blacklist написаны.
- [x] Profile endpoint написан.

### Permissions

- [x] `IsAuthenticated` применён к личным данным.
- [x] `AllowAny` применён к регистрации и чтению каталога.
- [x] Написаны простые permissions для Manager/Admin.
- [x] Написан `IsOwnerOrReadOnly`.
- [x] Личные querysets фильтруются по текущему user.

### Business logic

- [x] Корзина считает `item_total`, `subtotal` и общее количество.
- [x] Добавлена простая проверка stock.
- [x] Добавлена проверка quantity.
- [x] Повторный товар увеличивает quantity вместо создания дубликата.
- [x] Добавлен endpoint очистки корзины.
- [x] Заказ создаётся из корзины.
- [x] Stock уменьшается при заказе.
- [x] Создание заказа выполняется внутри `transaction.atomic()`.
- [x] Корзина после заказа очищается.
- [x] Общая цена PCBuild автоматически считается.
- [x] При сохранении PCBuild проверяются доступные правила совместимости.
- [x] Добавлен отдельный compatibility endpoint.
- [x] Laptop recommendation написана без внешнего AI.
- [x] PC recommendation написана без внешнего AI.

### Documentation and tests

- [x] Swagger подключён.
- [x] ReDoc подключён.
- [x] JWT Authorize в Swagger настроен.
- [x] Написаны базовые тесты регистрации, JWT, каталога, ролей и корзины.
- [ ] README с командами запуска не создан.
- [ ] Server не запускался для финальной проверки.

### Frontend and 3D

- [ ] Frontend не создан.
- [ ] Three.js не подключён.
- [ ] 3D-модель ПК не добавлена.
- [ ] Exploded view не реализован.
- [ ] Клики по деталям и панель характеристик не реализованы.
- [ ] Управление жестами через камеру не реализовано.

---

## 5. Текущий статус

| Часть | Статус |
|---|---|
| Django project | DONE |
| `myapp` | DONE |
| Settings | BASIC DONE |
| Models | FIRST SIMPLE VERSION DONE |
| Migrations for current models | DONE |
| Admin | DONE |
| Serializers | DONE |
| Views / ViewSets | DONE |
| URLs без Router | DONE |
| JWT | BASIC DONE |
| Permissions | BASIC DONE |
| Product API | NOT DONE |
| Reviews API | NOT DONE |
| Wishlist API | NOT DONE |
| Compare API | NOT DONE |
| Cart API | NOT DONE |
| Orders API | NOT DONE |
| PC Builder API | NOT DONE |
| Compatibility | NOT DONE |
| Recommendations | DONE |
| Swagger | DONE |
| Tests | BASIC DONE |
| Frontend | NOT STARTED |
| 3D viewer | NOT STARTED |

---

## 6. Следующий этап

Логичный следующий шаг:

1. Добавить управление статусами заказов для Manager/Admin.
2. Проверить и дополнить API избранного, сравнения и отзывов.

---

## 7. Важно

Этот файл описывает фактическое состояние проекта на момент создания `exam.md`.

Галочка `[x]` означает, что код уже есть.

Пустая галочка `[ ]` означает, что эта часть ещё не написана.

---

## 8. Выбранный 3D-дизайн

В качестве главного референса для будущего frontend выбран:

- **PC Anatomy**: <https://pc-anatomy.com/>
- GitHub: <https://github.com/Yoosseph/pc-anatomy>

Будущий frontend должен иметь похожую механику:

- [ ] Показ собранного компьютера в 3D.
- [ ] Вращение, приближение и перемещение камеры.
- [ ] Exploded view: плавное разделение компьютера на детали.
- [ ] Автоматическая анимация разборки и сборки.
- [ ] Выбор детали кликом.
- [ ] Подсветка выбранной детали.
- [ ] Панель с названием, описанием, ценой и характеристиками детали.
- [ ] Скрытие корпуса для просмотра внутренних компонентов.
- [ ] Подписи компонентов.
- [ ] Кнопка возврата в исходное состояние.

Этот дизайн относится к будущему frontend. В текущий backend его добавлять не нужно.

---

## 9. Правила Git и GitHub

После каждого завершённого изменения нужно сразу сохранять результат в Git и отправлять его в GitHub.

Отдельный commit нужно делать, когда:

- создан новый файл;
- завершена отдельная часть проекта;
- исправлена ошибка;
- изменены модели;
- добавлены migrations;
- добавлен API endpoint;
- добавлены тесты;
- изменена документация.

Каждый commit должен:

1. Содержать только связанные изменения.
2. Иметь простое и понятное название, которое прямо говорит, что было сделано.
3. Создаваться только после проверки изменений.
4. Не включать `.venv`, `__pycache__`, `*.pyc`, `db.sqlite3`, media и секреты.

Примеры названий commit:

```text
Добавил модели
Исправил модели
Добавил миграции
Настроил админку
Добавил сериализаторы
Исправил корзину
Обновил exam.md
```

После создания commit его нужно отправить в подключённый GitHub-репозиторий.

В API нельзя использовать `router`. Маршруты нужно указывать вручную в `urls.py` через `path()`. Если используются `ModelViewSet`, методы указываются вручную через `as_view()`.

Перед commit и push нужно:

- проверить `git status`;
- просмотреть diff;
- запустить проверки проекта;
- не отправлять пароли, токены и другие секреты.

Если GitHub-репозиторий ещё не подключён, сначала нужно добавить remote, а затем делать push.
