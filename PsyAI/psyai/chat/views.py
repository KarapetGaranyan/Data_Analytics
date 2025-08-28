# chat/views.py
import json
import requests
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .models import User, ChatSession, Message, PaymentPlan, Payment, UserSubscription

# Попробуем импортировать ЮKassa
try:
    from yookassa import Configuration, Payment as YooPayment

    # Настройка ЮKassa
    Configuration.account_id = getattr(settings, 'YUKASSA_SHOP_ID', 'your-shop-id')
    Configuration.secret_key = getattr(settings, 'YUKASSA_SECRET_KEY', 'your-secret-key')
    YUKASSA_AVAILABLE = True
except ImportError:
    YUKASSA_AVAILABLE = False
    print("YooKassa не установлена. Установите: pip install yookassa")


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
    """Страница с тарифами"""
    try:
        plans = PaymentPlan.objects.filter(is_active=True).order_by('price')

        context = {
            'subscription_plans': plans.filter(plan_type='subscription'),
            'package_plans': plans.filter(plan_type='package'),
        }
    except:
        # Если модели PaymentPlan еще нет, показываем пустые планы
        context = {
            'subscription_plans': [],
            'package_plans': [],
        }

    return render(request, 'upgrade.html', context)


# ================= ФУНКЦИИ ДЛЯ ПЛАТЕЖЕЙ =================

@login_required
def create_payment_view(request, plan_id):
    """Создание платежа"""
    if not YUKASSA_AVAILABLE:
        messages.error(request, 'Система платежей временно недоступна. Установите библиотеку yookassa.')
        return redirect('upgrade')

    if request.method != 'POST':
        return redirect('upgrade')

    try:
        plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
        user = request.user

        # Создаем запись о платеже в нашей БД
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=plan.price
        )

        # Создаем платеж в ЮKassa
        yukassa_payment = YooPayment.create({
            "amount": {
                "value": str(plan.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri(f"/payments/success/{payment.id}/")
            },
            "capture": True,
            "description": f"Оплата тарифа {plan.name}",
            "metadata": {
                "payment_id": str(payment.id),
                "user_id": str(user.id),
                "plan_id": str(plan.id)
            }
        })

        # Сохраняем ID от ЮKassa
        payment.yukassa_payment_id = yukassa_payment.id
        payment.save()

        # Редиректим пользователя на страницу оплаты ЮKassa
        return redirect(yukassa_payment.confirmation.confirmation_url)

    except PaymentPlan.DoesNotExist:
        messages.error(request, 'Тарифный план не найден')
        return redirect('upgrade')
    except Exception as e:
        messages.error(request, f'Ошибка при создании платежа: {str(e)}')
        return redirect('upgrade')


@login_required
def payment_success_view(request, payment_id):
    """Страница успешной оплаты"""
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)

        # Проверяем статус платежа в ЮKassa
        if payment.yukassa_payment_id and YUKASSA_AVAILABLE:
            yukassa_payment = YooPayment.find_one(payment.yukassa_payment_id)

            if yukassa_payment.status == 'succeeded':
                # Активируем подписку/пакет
                activate_user_plan(payment)

                context = {
                    'payment': payment,
                    'success': True,
                    'message': f'Оплата прошла успешно! {payment.plan.name} активирован.'
                }
            else:
                context = {
                    'payment': payment,
                    'success': False,
                    'message': 'Платеж еще обрабатывается. Проверьте статус через несколько минут.'
                }
        else:
            context = {
                'success': False,
                'message': 'Ошибка при проверке платежа'
            }

    except Payment.DoesNotExist:
        context = {
            'success': False,
            'message': 'Платеж не найден'
        }
    except Exception as e:
        context = {
            'success': False,
            'message': f'Ошибка: {str(e)}'
        }

    return render(request, 'payments/success.html', context)


@csrf_exempt
def yukassa_webhook(request):
    """Webhook для уведомлений от ЮKassa"""
    if not YUKASSA_AVAILABLE:
        return HttpResponse(status=501)

    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        # Получаем данные от ЮKassa
        event_json = json.loads(request.body)

        # Проверяем тип события
        if event_json.get('event') != 'payment.succeeded':
            return HttpResponse(status=200)

        # Получаем данные о платеже
        payment_data = event_json.get('object', {})
        yukassa_payment_id = payment_data.get('id')

        if not yukassa_payment_id:
            return HttpResponse(status=400)

        # Находим платеж в нашей БД
        try:
            payment = Payment.objects.get(yukassa_payment_id=yukassa_payment_id)
        except Payment.DoesNotExist:
            return HttpResponse(status=404)

        # Обновляем статус платежа
        if payment_data.get('status') == 'succeeded':
            payment.status = 'succeeded'
            payment.processed_at = timezone.now()
            payment.save()

            # Активируем подписку/пакет
            activate_user_plan(payment)

        return HttpResponse(status=200)

    except Exception as e:
        print(f"Webhook error: {e}")
        return HttpResponse(status=500)


def activate_user_plan(payment):
    """Активация тарифного плана пользователя"""
    user = payment.user
    plan = payment.plan

    if plan.plan_type == 'subscription':
        # Подписочная модель
        expires_at = timezone.now() + timedelta(days=plan.duration_days or 30)

        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'expires_at': expires_at,
                'is_active': True
            }
        )

        if not created:
            # Продлеваем существующую подписку
            subscription.plan = plan
            subscription.expires_at = expires_at
            subscription.is_active = True
            subscription.save()

        # Активируем Premium статус
        user.is_premium = True
        user.save()

    elif plan.plan_type == 'package':
        # Пакетная модель - добавляем сообщения
        user.free_messages_left += (plan.messages_count or 0)
        user.save()


def payment_cancel_view(request):
    """Страница отмены платежа"""
    return render(request, 'payments/cancel.html')