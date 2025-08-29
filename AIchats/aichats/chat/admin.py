from django.contrib import admin
from .models import AIModel, Assistant

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_name', 'provider', 'is_active', 'order')
    list_filter = ('provider', 'is_active')
    list_editable = ('is_active', 'order')
    search_fields = ('name', 'api_name')

@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'order')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active', 'order')
        }),
        ('Промпт и роль', {
            'fields': ('prompt', 'role')
        }),
        ('Задачи', {
            'fields': ('task', 'task_description')
        }),
        ('Правила и критерии', {
            'fields': ('rules', 'criteria', 'evaluation_rubric')
        }),
        ('Дополнительные настройки', {
            'fields': ('key_references', 'explicit_reminders', 'rule_additional_privacy', 'additional_guidelines'),
            'classes': ('collapse',)
        })
    )