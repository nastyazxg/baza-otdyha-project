# База Отдыха — Информационная система бронирования домиков и беседок

Учебный проект по практике. Django 5.1 + SQLite.

## Структура проекта

- **config/** — приложение Django со всеми моделями, представлениями и формами
  - `models.py` — 13 моделей (Category, Accommodation, SeasonalTariff, Booking и др.)
  - `views.py` — представления для всех страниц сайта
  - `forms.py` — формы регистрации и бронирования
  - `urls.py` — маршруты
  - `admin.py` — настройка админки
  - `fixtures/initial_data.json` — тестовые данные (30 объектов, 60 тарифов)
- **templates/** — HTML-шаблоны (base, home, catalog, object_detail, about, contacts, register, login, profile, search)
- **static/css/style.css** — единый файл стилей с CSS-переменными из UI-kit
- **static/js/main.js** — клиентская логика (бургер-меню, валидация, AJAX)
- **static/img/** — изображения для страниц
- **db.sqlite3** — база данных SQLite

## Запуск

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py loaddata initial_data.json
python3 manage.py runserver