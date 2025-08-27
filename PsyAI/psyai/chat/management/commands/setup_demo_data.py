from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from chat.models import ChatSession, Message

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание демо-данных для тестирования'

    def handle(self, *args, **options):
        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'free_messages_left': 3,
                'is_premium': False
            }
        )

        if created:
            user.set_password('demo123')
            user.save()

            # Создаем тестовую сессию
            session = ChatSession.objects.create(user=user)

            # Добавляем несколько сообщений
            messages = [
                ("Привет! Как дела?", True),
                ("Здравствуйте! Я ваш ИИ-психолог. Расскажите, что вас беспокоит?", False),
                ("У меня стресс на работе", True),
                (
                "Понимаю, что стресс на работе может быть очень тяжелым. Можете рассказать подробнее о том, что именно вызывает у вас стресс?",
                False),
            ]

            for content, is_user in messages:
                Message.objects.create(
                    session=session,
                    content=content,
                    is_user=is_user
                )

            self.stdout.write(
                self.style.SUCCESS(
                    'Демо-данные созданы:\n'
                    'Пользователь: demo_user\n'
                    'Пароль: demo123'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Демо-пользователь уже существует')
            )