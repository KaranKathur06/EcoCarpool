from django.urls import path
from . import views

app_name = 'payments'  # Add this namespace

urlpatterns = [
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/add-money/', views.add_money, name='add-money'),
    path('wallet/withdraw-money/', views.withdraw_money, name='withdraw-money'),
    path('transaction/<int:pk>/', views.transaction_detail, name='transaction-detail'),
    path('transaction/history/', views.TransactionHistoryView.as_view(), name='transaction-history'),
    path('history/', views.TransactionHistoryView.as_view(), name='history'),
    path('', views.payment_list, name='payment-list'),
    path('<int:pk>/', views.payment_detail, name='payment-detail'),
    # ... other payment URLs ...
]
