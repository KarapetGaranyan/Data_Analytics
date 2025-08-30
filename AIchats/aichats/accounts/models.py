from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    free_messages_used = models.IntegerField(default=0)

    def get_available_messages(self):
        from django.conf import settings
        return max(0, settings.FREE_MESSAGES_COUNT - self.free_messages_used)

    def can_send_message(self):
        from django.conf import settings
        return self.get_available_messages() > 0 or self.balance >= settings.MESSAGE_PRICE

    def charge_for_message(self):
        from django.conf import settings
        from decimal import Decimal

        if self.get_available_messages() > 0:
            self.free_messages_used += 1
        else:
            self.balance -= Decimal(str(settings.MESSAGE_PRICE))  # Конвертируем в Decimal

        self.save()


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('topup', 'Пополнение'),
        ('message', 'Отправка сообщения'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    PAYMENT_STATUSES = [
        ('pending', 'Ожидание'),
        ('succeeded', 'Успешно'),
        ('canceled', 'Отменено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    yookassa_payment_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Payment)
def process_payment(sender, instance, **kwargs):
    """Обрабатывает успешный платеж"""
    if instance.status == 'succeeded' and kwargs.get('update_fields') is None:
        # Проверяем, не был ли уже обработан этот платеж
        existing_transaction = Transaction.objects.filter(
            user=instance.user,
            transaction_type='topup',
            description__contains=f'ЮKassa ID: {instance.yookassa_payment_id}'
        ).exists()

        if not existing_transaction:
            # Пополняем баланс
            instance.user.balance += instance.amount
            instance.user.save()

            # Создаем транзакцию
            Transaction.objects.create(
                user=instance.user,
                transaction_type='topup',
                amount=instance.amount,
                description=f'Пополнение через ЮKassa ID: {instance.yookassa_payment_id}'
            )