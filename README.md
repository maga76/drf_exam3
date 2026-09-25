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

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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

- `/api/categories/`
- `/api/products/`
- `/api/reviews/`
- `/api/wishlist/`
- `/api/compare/`
- `/api/carts/`
- `/api/cart-items/`
- `/api/cart/clear/`
- `/api/orders/`
- `/api/pc-builds/`
- `/api/compatibility/check/`
- `/api/recommendations/laptops/`
- `/api/recommendations/pc/`

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
