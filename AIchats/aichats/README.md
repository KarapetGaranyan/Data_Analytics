# AI Chats

Универсальная веб-платформа для общения с различными AI-ассистентами. Поддерживает множество моделей ИИ (GPT, Claude, DeepSeek, Gemini) и специализированных ассистентов.

## Возможности

### Основные функции
- Чат с различными AI моделями (OpenAI, Anthropic, DeepSeek, Google)
- Специализированные ассистенты (Психолог, Программист, Учитель)
- Поддержка изображений в чате (для мультимодальных моделей)
- Система регистрации и аутентификации пользователей
- Баланс пользователей с бесплатными и платными сообщениями
- Интеграция с ЮKassa для пополнения баланса
- История транзакций и использования

### Поддерживаемые модели ИИ
- **OpenAI**: GPT-4o, GPT-4o Mini
- **Anthropic**: Claude Sonnet 4, Claude 3.5 Sonnet
- **DeepSeek**: DeepSeek Chat, DeepSeek Reasoner
- **Google**: Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.0 Flash

### Особенности ассистентов
Каждый ассистент настраивается через детальную структуру промптов:
- Основной промпт и роль
- Задачи и описание
- Правила поведения
- Критерии и рубрики оценивания
- Дополнительные инструкции и правила приватности

## Установка и запуск

### Требования
- Python 3.8+
- Django 4.2.7
- SQLite (по умолчанию)

### Установка

1. **Клонировать репозиторий**
```bash
git clone <repository-url>
cd aichats
```

2. **Создать виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установить зависимости**
```bash
pip install -r requirements.txt
```

4. **Настроить переменные окружения**
Создайте файл `.env` в корне проекта:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
PROXYAPI_TOKEN=your-proxyapi-token
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
```

5. **Выполнить миграции**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Создать суперпользователя**
```bash
python manage.py createsuperuser
```

7. **Загрузить тестовые данные**
```bash
python manage.py load_models
```

8. **Запустить сервер**
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

## Конфигурация

### ProxyAPI
Для работы с AI моделями используется сервис ProxyAPI.ru:
1. Зарегистрируйтесь на https://proxyapi.ru/
2. Получите токен доступа
3. Добавьте токен в файл `.env`

### ЮKassa (опционально)
Для приема платежей:
1. Зарегистрируйтесь на https://yookassa.ru/
2. Создайте магазин и получите Shop ID и Secret Key
3. Настройте webhook URL: `https://yourdomain.com/accounts/webhook/`
4. Добавьте данные в `.env`

### Структура файлов

```
aichats/
├── manage.py
├── requirements.txt
├── .env
├── aichats/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py      # Модели пользователей, транзакций, платежей
│   ├── views.py       # Регистрация, авторизация, платежи
│   ├── forms.py       # Формы регистрации и пополнения
│   └── admin.py       # Админ-панель для пользователей
├── chat/
│   ├── models.py      # Модели AI и ассистентов
│   ├── views.py       # API чата и загрузка изображений
│   ├── admin.py       # Управление моделями и ассистентами
│   └── templates/     # Шаблоны чата
├── templates/
│   ├── base.html      # Базовый шаблон
│   ├── accounts/      # Шаблоны авторизации
│   └── registration/  # Шаблоны входа/регистрации
└── media/             # Загруженные изображения
```

## Использование

### Для пользователей
1. Зарегистрируйтесь на сайте
2. Получите 5 бесплатных сообщений
3. Выберите модель ИИ и ассистента
4. Начните общение в чате
5. При необходимости пополните баланс

### Для администраторов
1. Войдите в админ-панель: http://127.0.0.1:8000/admin/
2. Управляйте моделями ИИ в разделе "AI Модели"
3. Создавайте и настраивайте ассистентов в разделе "Ассистенты"
4. Просматривайте пользователей и транзакции
5. Обрабатывайте платежи при необходимости

## Технические детали

### Архитектура
- **Backend**: Django + Django REST Framework
- **Frontend**: Django Templates + Bootstrap 5 + JavaScript
- **База данных**: SQLite (легко заменяется на PostgreSQL)
- **AI API**: ProxyAPI.ru для доступа к различным моделям
- **Платежи**: ЮKassa API
- **Файлы**: Локальное хранение в media/

### Безопасность
- CSRF защита для всех форм
- Аутентификация пользователей
- Валидация загружаемых файлов
- Ограничения на размер изображений (10MB)
- Безопасная обработка платежных данных

### API Endpoints
- `GET /` - Главная страница чата
- `POST /api/chat/` - Отправка сообщений в чат
- `POST /upload-image/` - Загрузка изображений
- `GET /accounts/profile/` - Профиль пользователя
- `POST /accounts/webhook/` - Webhook для ЮKassa

## Разработка

### Добавление новых моделей ИИ
1. Войдите в админ-панель
2. Перейдите в раздел "AI Модели"
3. Нажмите "Добавить AI Модель"
4. Укажите название, API имя и провайдера
5. При необходимости обновите логику в `chat/views.py`

### Создание ассистентов
1. Используйте админ-панель для создания
2. Заполните все поля структуры промпта
3. Установите порядок сортировки
4. Активируйте ассистента

### Локальное тестирование платежей
Для тестирования webhook ЮKassa на localhost используйте ngrok:
```bash
ngrok http 8000
```
Используйте полученный URL в настройках ЮKassa.

## Деплой

### Подготовка к продакшену
1. Измените `DEBUG = False` в настройках
2. Настройте `ALLOWED_HOSTS`
3. Используйте PostgreSQL вместо SQLite
4. Настройте статические файлы через nginx
5. Используйте gunicorn для WSGI
6. Настройте HTTPS

### Переменные окружения для продакшена
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/dbname
PROXYAPI_TOKEN=your-proxyapi-token
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-live-secret-key
```

## Лицензия

MIT License

## Поддержка

Для вопросов и предложений создавайте issue в репозитории или обращайтесь к разработчикам.