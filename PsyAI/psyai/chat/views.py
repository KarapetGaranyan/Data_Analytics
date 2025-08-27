# chat/views.py
import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import User, ChatSession, Message


def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь уже существует')
            return render(request, 'auth/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Регистрация успешна! У вас есть 5 бесплатных сообщений.')
        return redirect('chat')

    return render(request, 'auth/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat')
        else:
            messages.error(request, 'Неверные данные для входа')

    return render(request, 'auth/login.html')


@login_required
def chat_view(request):
    # Получаем или создаем активную сессию
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        is_active=True
    )

    messages_list = session.messages.all()

    context = {
        'session': session,
        'messages': messages_list,
        'free_messages_left': request.user.free_messages_left,
        'is_premium': request.user.is_premium,
    }

    return render(request, 'chat/chat.html', context)


@csrf_exempt
@login_required
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    user = request.user

    # Проверяем лимиты
    if not user.is_premium and user.free_messages_left <= 0:
        return JsonResponse({
            'error': 'Бесплатные сообщения закончились',
            'need_premium': True
        }, status=403)

    data = json.loads(request.body)
    user_message = data.get('message', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Пустое сообщение'}, status=400)

    # Получаем активную сессию
    session = ChatSession.objects.filter(user=user, is_active=True).first()
    if not session:
        session = ChatSession.objects.create(user=user)

    # Сохраняем сообщение пользователя
    Message.objects.create(
        session=session,
        content=user_message,
        is_user=True
    )

    # Уменьшаем счетчик бесплатных сообщений
    if not user.is_premium:
        user.free_messages_left -= 1
        user.save()

    # Получаем ответ от ИИ
    ai_response = get_ai_response(user_message)

    # Сохраняем ответ ИИ
    Message.objects.create(
        session=session,
        content=ai_response,
        is_user=False
    )

    return JsonResponse({
        'ai_response': ai_response,
        'free_messages_left': user.free_messages_left,
        'is_premium': user.is_premium
    })


def get_ai_response(user_message):
    """Получаем ответ от ProxyAPI GPT"""
    try:
        url = "https://api.proxyapi.ru/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.PROXYAPI_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты опытный психолог. Отвечай эмпатично, поддерживающе и профессионально. Помогай людям разобраться в их эмоциях и переживаниях."
                },
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return "Извините, произошла техническая ошибка. Попробуйте еще раз."

    except Exception as e:
        print(f"AI API Error: {e}")
        return "К сожалению, сейчас я не могу ответить. Попробуйте позже."


def upgrade_view(request):
    """Заглушка для апгрейда до Premium"""
    if request.method == 'POST':
        # Имитируем успешную оплату
        user = request.user
        user.is_premium = True
        user.save()
        messages.success(request, 'Поздравляем! Теперь у вас Premium доступ.')
        return redirect('chat')

    return render(request, 'upgrade.html')