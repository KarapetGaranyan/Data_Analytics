from django.core.management.base import BaseCommand
from chat.models import AIModel, Assistant


class Command(BaseCommand):
    help = 'Загружает базовые модели и ассистентов'

    def handle(self, *args, **options):
        # Создаем модели
        models_data = [
            {'name': 'GPT-4o', 'api_name': 'gpt-4o', 'provider': 'openai', 'description': 'Лучшая модель OpenAI'},
            {'name': 'GPT-4o Mini', 'api_name': 'gpt-4o-mini', 'provider': 'openai',
             'description': 'Быстрая модель OpenAI'},
            {'name': 'Claude Sonnet 4', 'api_name': 'claude-sonnet-4-20250514', 'provider': 'anthropic',
             'description': 'Новейшая модель Claude'},
            {'name': 'Claude 3.5 Sonnet', 'api_name': 'claude-3-5-sonnet-20241022', 'provider': 'anthropic',
             'description': 'Отличная модель для кода'},
            {'name': 'DeepSeek Chat', 'api_name': 'deepseek-chat', 'provider': 'deepseek',
             'description': 'Бесплатная модель DeepSeek'},
            {'name': 'DeepSeek Reasoner', 'api_name': 'deepseek-reasoner', 'provider': 'deepseek',
             'description': 'Рассуждающая модель DeepSeek'},
            {'name': 'Gemini 2.5 Pro', 'api_name': 'gemini-2.5-pro', 'provider': 'google',
             'description': 'Топовая модель Google с контекстом 1M токенов'},
            {'name': 'Gemini 2.5 Flash', 'api_name': 'gemini-2.5-flash', 'provider': 'google',
             'description': 'Быстрая мультимодальная модель Google'},
            {'name': 'Gemini 2.0 Flash', 'api_name': 'gemini-2.0-flash', 'provider': 'google',
             'description': 'Новая быстрая модель Google'},
        ]

        for i, model_data in enumerate(models_data):
            model, created = AIModel.objects.get_or_create(
                api_name=model_data['api_name'],
                defaults={**model_data, 'order': i}
            )
            if created:
                self.stdout.write(f'Создана модель: {model.name}')
            else:
                self.stdout.write(f'Модель уже существует: {model.name}')

        # Создаем ассистентов
        assistants_data = [
            {
                'name': 'Психолог',
                'description': 'Помогу разобраться с эмоциями и стрессом',
                'prompt': 'Ты опытный психолог. Веди себя эмпатично, задавай уточняющие вопросы, помогай разобраться в эмоциях.',
                'role': 'Психолог-консультант',
                'task': 'Оказание психологической поддержки',
                'rules': 'Не ставь диагнозы, не давай медицинские советы, при серьезных проблемах рекомендуй обратиться к специалисту',
                'order': 0
            },
            {
                'name': 'Программист',
                'description': 'Помогу с кодом и техническими вопросами',
                'prompt': 'Ты опытный программист. Помогай писать код, объясняй концепции, исправляй ошибки. Всегда используй блоки кода с указанием языка программирования для лучшего отображения.',
                'role': 'Senior разработчик',
                'task': 'Помощь в программировании',
                'rules': 'Всегда объясняй код, предлагай лучшие практики, учитывай производительность и безопасность. Используй markdown форматирование для структурированных ответов.',
                'order': 1
            },
            {
                'name': 'Учитель',
                'description': 'Объясню сложные темы простыми словами',
                'prompt': 'Ты терпеливый учитель. Объясняй сложные вещи простыми словами, приводи примеры. Используй структурированные ответы с заголовками и списками для лучшего понимания.',
                'role': 'Преподаватель',
                'task': 'Обучение и объяснение материала',
                'rules': 'Используй простые примеры, проверяй понимание, поощряй вопросы. Структурируй ответы с помощью заголовков и списков.',
                'order': 2
            },
        ]

        for assistant_data in assistants_data:
            assistant, created = Assistant.objects.get_or_create(
                name=assistant_data['name'],
                defaults=assistant_data
            )
            if created:
                self.stdout.write(f'Создан ассистент: {assistant.name}')
            else:
                self.stdout.write(f'Ассистент уже существует: {assistant.name}')

        self.stdout.write(self.style.SUCCESS('Загрузка завершена!'))