# chat/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ChatSession, Message

from .models import PaymentPlan, Payment, UserSubscription

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


# Добавить в chat/admin.py




@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'messages_count', 'duration_days', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'plan__plan_type', 'created_at')
    search_fields = ('user__username', 'yukassa_payment_id')
    readonly_fields = ('id', 'yukassa_payment_id', 'created_at', 'updated_at')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'started_at', 'expires_at', 'is_active', 'is_expired_status')
    list_filter = ('is_active', 'plan', 'started_at')
    search_fields = ('user__username',)

    def is_expired_status(self, obj):
        return obj.is_expired()

    is_expired_status.boolean = True
    is_expired_status.short_description = 'Истекла'