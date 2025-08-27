from django.core.management.base import BaseCommand
from chat.models import User


class Command(BaseCommand):
    help = 'Сброс бесплатных сообщений для всех пользователей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--messages',
            type=int,
            default=5,
            help='Количество бесплатных сообщений для сброса (по умолчанию 5)'
        )

    def handle(self, *args, **options):
        messages_count = options['messages']

        # Сбрасываем только для не-премиум пользователей
        users = User.objects.filter(is_premium=False)
        updated_count = users.update(free_messages_left=messages_count)

        self.stdout.write(
            self.style.SUCCESS(
                f'Сброшено {messages_count} бесплатных сообщений для {updated_count} пользователей'
            )
        )