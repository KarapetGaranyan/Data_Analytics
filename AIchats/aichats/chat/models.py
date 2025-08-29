from django.db import models


class AIModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    api_name = models.CharField(max_length=100, verbose_name="API название")
    description = models.TextField(blank=True, verbose_name="Описание")
    provider = models.CharField(max_length=50, choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('deepseek', 'DeepSeek'),
        ('google', 'Google'),
    ], verbose_name="Провайдер")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "AI Модель"
        verbose_name_plural = "AI Модели"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Assistant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    prompt = models.TextField(verbose_name="Системный промпт")
    role = models.TextField(blank=True, verbose_name="Роль")
    task = models.TextField(blank=True, verbose_name="Задача")
    task_description = models.TextField(blank=True, verbose_name="Описание задачи")
    rules = models.TextField(blank=True, verbose_name="Правила")
    key_references = models.TextField(blank=True, verbose_name="Ключевые ссылки")
    criteria = models.TextField(blank=True, verbose_name="Критерии")
    evaluation_rubric = models.TextField(blank=True, verbose_name="Рубрика оценивания")
    explicit_reminders = models.TextField(blank=True, verbose_name="Явные напоминания")
    rule_additional_privacy = models.TextField(blank=True, verbose_name="Дополнительные правила приватности")
    additional_guidelines = models.TextField(blank=True, verbose_name="Дополнительные руководящие принципы")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Ассистент"
        verbose_name_plural = "Ассистенты"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_full_prompt(self):
        """Собирает полный промпт из всех полей"""
        parts = []
        if self.prompt:
            parts.append(f"ОСНОВНОЙ ПРОМПТ:\n{self.prompt}")
        if self.role:
            parts.append(f"РОЛЬ:\n{self.role}")
        if self.task:
            parts.append(f"ЗАДАЧА:\n{self.task}")
        if self.task_description:
            parts.append(f"ОПИСАНИЕ ЗАДАЧИ:\n{self.task_description}")
        if self.rules:
            parts.append(f"ПРАВИЛА:\n{self.rules}")
        if self.key_references:
            parts.append(f"КЛЮЧЕВЫЕ ССЫЛКИ:\n{self.key_references}")
        if self.criteria:
            parts.append(f"КРИТЕРИИ:\n{self.criteria}")
        if self.evaluation_rubric:
            parts.append(f"РУБРИКА ОЦЕНИВАНИЯ:\n{self.evaluation_rubric}")
        if self.explicit_reminders:
            parts.append(f"ЯВНЫЕ НАПОМИНАНИЯ:\n{self.explicit_reminders}")
        if self.rule_additional_privacy:
            parts.append(f"ДОПОЛНИТЕЛЬНЫЕ ПРАВИЛА ПРИВАТНОСТИ:\n{self.rule_additional_privacy}")
        if self.additional_guidelines:
            parts.append(f"ДОПОЛНИТЕЛЬНЫЕ РУКОВОДЯЩИЕ ПРИНЦИПЫ:\n{self.additional_guidelines}")

        return "\n\n".join(parts)