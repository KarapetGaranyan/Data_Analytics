from flask import Flask, render_template, jsonify
import requests
import random
import os

app = Flask(__name__)

# API ключ для API Ninjas (можно установить через переменную окружения)
API_NINJAS_KEY = os.environ.get('API_NINJAS_KEY', 'JZusOqIAmDsUywKG5BpzOg==1kZe4r965J5UpBQn')


# Список API для получения цитат
def get_quote_apis():
    apis = [
        {
            'name': 'ZenQuotes',
            'url': 'https://zenquotes.io/api/random',
            'parser': lambda data: {'text': data[0]['q'], 'author': data[0]['a']} if data and len(data) > 0 else None,
            'headers': {}
        },
        {
            'name': 'QuoteSlate',
            'url': 'https://quoteslate.vercel.app/api/quotes/random',
            'parser': lambda data: {'text': data['quote'],
                                    'author': data['author']} if data and 'quote' in data else None,
            'headers': {}
        }
    ]

    # Добавляем API Ninjas только если есть API ключ
    if API_NINJAS_KEY:
        apis.append({
            'name': 'API Ninjas',
            'url': 'https://api.api-ninjas.com/v1/quotes',
            'parser': lambda data: {'text': data[0]['quote'], 'author': data[0]['author']} if data and len(
                data) > 0 else None,
            'headers': {'X-Api-Key': API_NINJAS_KEY}
        })

    return apis


def get_random_quote():
    """Получает случайную цитату из одного из доступных API"""
    # Получаем актуальный список API
    apis = get_quote_apis()

    if not apis:
        print("Нет доступных API для получения цитат")
        return get_fallback_quote()

    # Перемешиваем список API для случайного порядка
    random.shuffle(apis)

    # Пробуем каждый API по очереди
    for api in apis:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            headers.update(api.get('headers', {}))

            response = requests.get(api['url'], timeout=10, headers=headers)
            response.raise_for_status()
            data = response.json()

            parsed_quote = api['parser'](data)
            if parsed_quote and parsed_quote.get('text') and parsed_quote.get('author'):
                print(f"Успешно получена цитата из {api['name']}")
                return parsed_quote

        except Exception as e:
            print(f"Ошибка при получении цитаты из {api['name']}: {e}")
            continue

    # Если все API недоступны, возвращаем резервную цитату
    return get_fallback_quote()


def get_fallback_quote():
    """Возвращает случайную резервную цитату"""
    fallback_quotes = [
        {'text': 'Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма.',
         'author': 'Уинстон Черчилль'},
        {'text': 'Жизнь — это то, что происходит с тобой, пока ты строишь планы.', 'author': 'Джон Леннон'},
        {'text': 'Будь собой, остальные роли уже заняты.', 'author': 'Оскар Уайльд'},
        {'text': 'Единственный способ делать великую работу — любить то, что ты делаешь.', 'author': 'Стив Джобс'},
        {'text': 'Не бойтесь совершить ошибку. Бойтесь не попытаться.', 'author': 'Неизвестен'},
        {
            'text': 'Величайшая слава не в том, чтобы никогда не падать, а в том, чтобы подниматься каждый раз после падения.',
            'author': 'Конфуций'},
        {'text': 'Будущее принадлежит тем, кто верит в красоту своих мечтаний.', 'author': 'Элеонора Рузвельт'},
        {'text': 'Измените свои мысли, и вы измените свой мир.', 'author': 'Норман Винсент Пил'}
    ]

    return random.choice(fallback_quotes)


@app.route('/')
def index():
    """Главная страница с цитатой"""
    quote = get_random_quote()
    return render_template('index.html', quote=quote)


@app.route('/api/quote')
def api_quote():
    """API endpoint для получения цитаты в формате JSON"""
    quote = get_random_quote()
    return jsonify(quote)


if __name__ == '__main__':
    app.run(debug=True)