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

- [ ] Новая migration для текущего `models.py` не создана.
- [ ] Текущие модели не применены к `db.sqlite3`.
- [ ] Тестовые данны не созданы.

Важно: файл `db.sqlite3` существует, но он был создан до последнего упрощения `models.py`. Поэтому его схема может не совпадать с текущими моделями.

### Django Admin

- [ ] Модели не зарегистрированы в `admin.py`.
- [ ] Superuser не создан в текущей версии базы.

### API

- [ ] Django REST Framework не подключён в `INSTALLED_APPS`.
- [ ] `serializers.py` не создан.
- [ ] `ModelSerializer` не написаны.
- [ ] `ModelViewSet` не написаны.
- [ ] Router не настроен.
- [ ] API URLs не созданы.
- [ ] CRUD endpoints не работают.
- [ ] Поиск, фильтры, ordering и pagination не написаны.

### Authentication

- [ ] Register endpoint не написан.
- [ ] Login endpoint не написан.
- [ ] JWT authentication не настроена.
- [ ] Access/refresh tokens не подключены.
- [ ] Logout и blacklist не написаны.
- [ ] Profile endpoint не написан.

### Permissions

- [ ] `IsAuthenticated` не применён.
- [ ] `AllowAny` не применён.
- [ ] Manager/Admin permissions не написаны.
- [ ] Owner permissions не написаны.
- [ ] Querysets не фильтруются по текущему user.

### Business logic

- [ ] Корзина не считает subtotal.
- [ ] Нет проверки stock.
- [ ] Нет проверки quantity.
- [ ] Заказ не создаётся из корзины.
- [ ] Stock не уменьшается при заказе.
- [ ] `transaction.atomic()` не используется.
- [ ] Корзина после заказа не очищается.
- [ ] Общая цена PCBuild автоматически не считается.
- [ ] Compatibility check не написан.
- [ ] Laptop recommendation не написана.
- [ ] PC recommendation не написана.

### Documentation and tests

- [ ] Swagger не подключён.
- [ ] Redoc не подключён.
- [ ] JWT Authorize в Swagger не настроен.
- [ ] Тесты не написаны.
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
| Migrations for current models | NOT DONE |
| Admin | NOT DONE |
| Serializers | NOT DONE |
| Views / ViewSets | NOT DONE |
| URLs / Router | NOT DONE |
| JWT | NOT DONE |
| Permissions | NOT DONE |
| Product API | NOT DONE |
| Reviews API | NOT DONE |
| Wishlist API | NOT DONE |
| Compare API | NOT DONE |
| Cart API | NOT DONE |
| Orders API | NOT DONE |
| PC Builder API | NOT DONE |
| Compatibility | NOT DONE |
| Recommendations | NOT DONE |
| Swagger | NOT DONE |
| Tests | NOT DONE |
| Frontend | NOT STARTED |
| 3D viewer | NOT STARTED |

---

## 6. Следующий этап

Логичный следующий шаг:

1. Проверить модели с преподавателем.
2. Выполнить `python manage.py makemigrations`.
3. Выполнить `python manage.py migrate`.
4. Зарегистрировать модели в `admin.py`.
5. Только после этого переходить к serializers и API.

---

## 7. Важно

Этот файл описывает фактическое состояние проекта на момент создания `exam.md`.

Галочка `[x]` означает, что код уже ест.

Пустая галочка `[ ]` означает, что эта часть ещё не написана.
