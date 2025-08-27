# PsyAI - ИИ Психолог MVP

Минимальная версия платформы для общения с ИИ-психологом.

## 🚀 Быстрый запуск

### 1. Клонирование и установка
```bash
git clone <your-repo>
cd psyai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка проекта
```bash
# Создать проект и приложение
django-admin startproject psyai .
python manage.py startapp chat

# Создать папки для шаблонов
mkdir -p templates/auth templates/chat static
```

### 3. Настройка переменных окружения
Создайте файл `.env`:
```
PROXYAPI_TOKEN=your_proxyapi_token_here
SECRET_KEY=your_secret_django_key_here
DEBUG=True
```

### 4. Применение миграций
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Создание демо-данных (опционально)
```bash
python manage.py setup_demo_data
```

### 6. Запуск
```bash
python manage.py runserver
```

Откройте http://127.0.0.1:8000

## 🎯 Основной функционал

### ✅ Реализовано в MVP:
- **Регистрация и вход** через email/username
- **Чат с ИИ-психологом** (GPT через ProxyAPI)
- **Система лимитов**: 5 бесплатных сообщений для новых пользователей
- **Premium заглушка**: кнопка активации Premium статуса
- **Адаптивный интерфейс** с Bootstrap
- **Админ-панель** для управления пользователями и чатами
- **История сообщений** сохраняется в базе данных

### 🔧 Технический стек:
- **Backend**: Django 4.2 + SQLite
- **Frontend**: Django Templates + Bootstrap 5 + Vanilla JS
- **ИИ**: ProxyAPI (GPT-3.5-turbo)
- **Стили**: Bootstrap 5

## 📝 Как пользоваться

### Для пользователей:
1. Зарегистрируйтесь на главной странице
2. Получите 5 бесплатных сообщений
3. Общайтесь с ИИ-психологом в чате
4. После исчерпания лимита - активируйте Premium (демо)

### Для администраторов:
1. Заходите в `/admin/` под суперпользователем
2. Управляйте пользователями, сессиями, сообщениями
3. Просматривайте статистику и активность

## 🔧 Управляющие команды

```bash
# Сброс бесплатных сообщений всем пользователям
python manage.py reset_free_messages --messages 5

# Создание демо-пользователя (demo_user/demo123)  
python manage.py setup_demo_data
```

## 🎨 Кастомизация

### Изменить промпт ИИ-психолога:
В `chat/views.py`, функция `get_ai_response()`, измените системное сообщение:
```python
"content": "Ваш новый промпт для ИИ-психолога..."
```

### Изменить лимиты:
В `chat/models.py`, модель `User`:
```python
free_messages_left = models.IntegerField(default=10)  # вместо 5
```

### Настроить стили:
Отредактируйте CSS в `templates/base.html` или подключите свои стили.

## 🚀 Деплой

### На Railway:
```bash
pip install gunicorn
# Создать Procfile: web: gunicorn psyai.wsgi
# Создать runtime.txt: python-3.11.0
```

### На VPS:
```bash
pip install gunicorn
gunicorn psyai.wsgi:application --bind 0.0.0.0:8000
```

## 📊 Структура проекта
```
psyai/
├── psyai/
│   ├── settings.py      # Главные настройки
│   ├── urls.py          # Главный роутинг
│   └── wsgi.py
├── chat/
│   ├── models.py        # User, ChatSession, Message
│   ├── views.py         # Логика чата и auth
│   ├── urls.py          # Роуты приложения
│   ├── admin.py         # Админ-панель
│   └── management/      # Команды управления
├── templates/           # HTML шаблоны
├── static/             # CSS, JS, изображения
└── db.sqlite3          # База данных
```

## 🔄 Что добавить на 2-м этапе:

1. **Реальная оплата** (Stripe/ЮKassa)
2. **WebSocket чат** для реального времени  
3. **Улучшенный UI/UX**
4. **История чатов** в личном кабинете
5. **Экспорт диалогов**

## ⚠️ Важные заметки

- Замените `PROXYAPI_TOKEN` на реальный токен от ProxyAPI.ru
- В продакшене обязательно смените `SECRET_KEY` и отключите `DEBUG`
- Для продакшена используйте PostgreSQL вместо SQLite
- Добавьте HTTPS сертификат для безопасности

## 🐛 Тестирование

Демо-аккаунт (если создавали):
- **Логин**: demo_user  
- **Пароль**: demo123
- **Статус**: 3 бесплатных сообщения

## 📞 Поддержка

При возникновении проблем:
1. Проверьте, что все зависимости установлены
2. Убедитесь, что миграции применены
3. Проверьте, что PROXYAPI_TOKEN корректный
4. Посмотрите логи в консоли Django