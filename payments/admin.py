from django.contrib import admin
from .models import Payment, Wallet, Transaction, BankAccount

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payer', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payer__username', 'receiver__username', 'transaction_id']
    date_hierarchy = 'created_at'

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('wallet__user__username', 'wallet__user__email')

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'account_holder_name', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('user__username', 'user__email', 'bank_name', 'account_holder_name')