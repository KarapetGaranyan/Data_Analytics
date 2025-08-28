# chat/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

import uuid
from decimal import Decimal

class User(AbstractUser):
    free_messages_left = models.IntegerField(default=5)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat {self.id} - {self.user.username}"

class Message(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField()  # True = пользователь, False = ИИ
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        sender = "User" if self.is_user else "AI"
        return f"{sender}: {self.content[:50]}..."


class PaymentPlan(models.Model):
    """Тарифные планы"""
    PLAN_TYPES = (
        ('subscription', 'Подписка'),
        ('package', 'Пакет сообщений'),
    )

    name = models.CharField(max_length=100, verbose_name='Название')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    messages_count = models.IntegerField(null=True, blank=True, verbose_name='Количество сообщений')
    duration_days = models.IntegerField(null=True, blank=True, verbose_name='Длительность в днях')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price}₽"


class Payment(models.Model):
    """История платежей"""
    PAYMENT_STATUS = (
        ('pending', 'Ожидает оплаты'),
        ('succeeded', 'Успешно оплачен'),
        ('canceled', 'Отменен'),
        ('failed', 'Ошибка оплаты'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)

    # ЮKassa данные
    yukassa_payment_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Результат обработки
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Платеж {self.amount}₽ от {self.user.username} - {self.status}"


class UserSubscription(models.Model):
    """Подписки пользователей"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    auto_renew = models.BooleanField(default=False)

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} до {self.expires_at.date()}"