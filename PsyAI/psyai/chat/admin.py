# chat/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ChatSession, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'free_messages_left', 'is_premium', 'created_at', 'is_active')
    list_filter = ('is_premium', 'is_active', 'created_at')
    search_fields = ('username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('PsyAI Settings', {
            'fields': ('free_messages_left', 'is_premium')
        }),
    )


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_active', 'message_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username',)

    def message_count(self, obj):
        return obj.messages.count()

    message_count.short_description = 'Сообщений'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender_type', 'content_preview', 'timestamp')
    list_filter = ('is_user', 'timestamp')
    search_fields = ('content', 'session__user__username')

    def sender_type(self, obj):
        return 'Пользователь' if obj.is_user else 'ИИ'

    sender_type.short_description = 'Отправитель'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Содержание'