from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassa import Configuration, Payment as YooPayment
import json
import uuid

from .forms import SignUpForm, TopUpForm
from .models import User, Transaction, Payment


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request,
                             f'Добро пожаловать! У вас есть {settings.FREE_MESSAGES_COUNT} бесплатных сообщений.')
            return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    transactions = user.transactions.all()[:10]

    context = {
        'user': user,
        'transactions': transactions,
        'free_messages_left': user.get_available_messages(),
        'message_price': settings.MESSAGE_PRICE,
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def topup(request):
    if request.method == 'POST':
        form = TopUpForm(request.POST)
        if form.is_valid():
            amount = int(form.cleaned_data['amount'])

            # Проверяем настройки ЮKassa
            if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
                messages.error(request, 'Оплата временно недоступна. Обратитесь к администратору.')
                return redirect('topup')

            try:
                import requests
                import base64

                # Правильная Basic Auth для ЮKassa
                credentials = f"{settings.YOOKASSA_SHOP_ID}:{settings.YOOKASSA_SECRET_KEY}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()

                headers = {
                    'Authorization': f'Basic {encoded_credentials}',
                    'Content-Type': 'application/json',
                    'Idempotence-Key': str(uuid.uuid4())
                }

                data = {
                    "amount": {
                        "value": f"{amount}.00",
                        "currency": "RUB"
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": request.build_absolute_uri('/accounts/payment-success/')
                    },
                    "capture": True,
                    "description": f"Пополнение баланса пользователя {request.user.username}",
                    "metadata": {
                        "user_id": str(request.user.id)
                    }
                }

                response = requests.post(
                    'https://api.yookassa.ru/v3/payments',
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if response.status_code == 200:
                    payment_data = response.json()

                    # Сохраняем в базу
                    Payment.objects.create(
                        user=request.user,
                        amount=amount,
                        yookassa_payment_id=payment_data['id']
                    )

                    return redirect(payment_data['confirmation']['confirmation_url'])
                else:
                    messages.error(request, f'Ошибка создания платежа: {response.text}')
                    return redirect('topup')

            except Exception as e:
                messages.error(request, f'Ошибка при создании платежа: {str(e)}')
                return redirect('topup')
    else:
        form = TopUpForm()

    return render(request, 'accounts/topup.html', {'form': form})


@login_required
def payment_success(request):
    messages.success(request, 'Платеж обрабатывается. Баланс будет пополнен в течение нескольких минут.')
    return redirect('profile')


@csrf_exempt
@require_POST
def webhook(request):
    """Webhook для получения уведомлений от ЮKassa"""
    try:
        data = json.loads(request.body)
        payment_data = data.get('object', {})

        if payment_data.get('status') == 'succeeded':
            payment_id = payment_data.get('id')
            amount = float(payment_data.get('amount', {}).get('value', 0))
            user_id = payment_data.get('metadata', {}).get('user_id')

            if payment_id and user_id:
                try:
                    payment = Payment.objects.get(yookassa_payment_id=payment_id)
                    if payment.status != 'succeeded':
                        payment.status = 'succeeded'
                        payment.save()

                        # Пополняем баланс пользователя
                        user = payment.user
                        user.balance += amount
                        user.save()

                        # Создаем транзакцию
                        Transaction.objects.create(
                            user=user,
                            transaction_type='topup',
                            amount=amount,
                            description=f'Пополнение через ЮKassa'
                        )

                except Payment.DoesNotExist:
                    pass

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def payment_cancel(request):
    messages.warning(request, 'Платеж был отменен.')
    return redirect('profile')