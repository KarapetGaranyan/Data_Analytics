from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Transaction, Payment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'balance', 'free_messages_used', 'is_email_verified', 'date_joined')
    list_filter = ('is_email_verified', 'date_joined')
    search_fields = ('username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('balance', 'free_messages_used', 'is_email_verified')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'yookassa_payment_id')
    readonly_fields = ('created_at', 'updated_at')