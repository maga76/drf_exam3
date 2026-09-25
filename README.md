# PC Store Backend

Backend интернет-магазина компьютеров, ноутбуков и комплектующих на Django REST Framework.

## Возможности

- регистрация, JWT-вход, обновление токена и logout;
- профиль пользователя;
- роли `user`, `manager`, `admin`;
- каталог категорий и товаров;
- поиск, фильтры, сортировка и pagination;
- отзывы, избранное и сравнение товаров;
- корзина с проверкой количества и остатка;
- создание заказа из корзины;
- управление статусами заказов для Manager/Admin;
- сохранение сборок ПК;
- расчёт цены и проверка совместимости сборки;
- рекомендации ноутбуков и сборок ПК из реальных товаров базы;
- Swagger и ReDoc;
- автоматические тесты.

Frontend в этот репозиторий не входит. Он подключается к backend через REST API.

## Установка на Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

## Установка на Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

## Создание администратора

```bash
python manage.py createsuperuser
```

После создания пользователя его поле `role` можно изменить на `admin` через Django Admin.

## Запуск

```bash
python manage.py runserver
```

После запуска доступны:

- API: <http://127.0.0.1:8000/api/>
- Django Admin: <http://127.0.0.1:8000/admin/>
- Swagger: <http://127.0.0.1:8000/swagger/>
- ReDoc: <http://127.0.0.1:8000/redoc/>

## Авторизация

Основные endpoints:

- `POST /api/register/`
- `POST /api/login/`
- `POST /api/token/refresh/`
- `POST /api/logout/`
- `GET /api/profile/`
- `PATCH /api/profile/`

Для защищённых запросов передавайте access token:

```text
Authorization: Bearer access_token
```

## Основные API endpoints

| Method | URL | Назначение |
|---|---|---|
| POST | `/api/register/` | Регистрация |
| POST | `/api/login/` | Получение JWT |
| POST | `/api/token/refresh/` | Обновление access token |
| POST | `/api/logout/` | Выход и blacklist refresh token |
| GET, PATCH | `/api/profile/` | Профиль текущего пользователя |
| GET, POST | `/api/categories/` | Категории |
| GET, POST | `/api/products/` | Товары |
| GET, POST | `/api/reviews/` | Отзывы |
| GET, POST | `/api/wishlist/` | Избранное |
| GET, POST | `/api/compare/` | Сравнение |
| GET | `/api/carts/` | Корзина текущего пользователя |
| GET, POST | `/api/cart-items/` | Позиции корзины |
| DELETE | `/api/cart/clear/` | Очистка корзины |
| GET, POST | `/api/orders/` | Заказы текущего пользователя |
| PATCH | `/api/orders/{id}/status/` | Изменение статуса Manager/Admin |
| GET, POST | `/api/pc-builds/` | Сохранённые сборки ПК |
| POST | `/api/compatibility/check/` | Проверка совместимости |
| POST | `/api/recommendations/laptops/` | Рекомендация ноутбуков |
| POST | `/api/recommendations/pc/` | Рекомендация сборки ПК |
| GET | `/api/admin/users/` | Список пользователей для Admin |
| GET, PATCH | `/api/admin/users/{id}/` | Управление пользователем Admin |
| GET | `/api/admin/orders/` | Все заказы Manager/Admin |

URL написаны вручную через `path()` и `as_view()`. DRF router не используется.

## Фильтры товаров

Примеры:

```text
/api/products/?search=rtx
/api/products/?product_type=gpu
/api/products/?brand=MSI
/api/products/?category=1
/api/products/?min_price=100&max_price=1000
/api/products/?in_stock=true
/api/products/?ordering=price
```

## Тесты

```bash
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

## База данных

На текущем этапе используется SQLite. Файлы базы, виртуальное окружение, media и секреты не отправляются в GitHub.

Тестовые товары можно создать через Django Admin или Swagger. Отдельный сложный seeder не используется.
