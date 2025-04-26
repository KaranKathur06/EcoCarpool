from django.shortcuts import render, redirect, get_object_or_404
from .models import UserPayment
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Transaction, Wallet, BankAccount
from django.db.models import Sum, Q
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

# Create your views here.

from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the payments app!")

@login_required
def payment_list(request):
    # Get all payments ordered by date
    payment_list = UserPayment.objects.all().order_by('-created_at')
    
    # Add pagination
    paginator = Paginator(payment_list, 10)  # Show 10 payments per page
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    return render(request, 'payments/list.html', {'payments': payments})

def payment_detail(request, pk):
    payment = UserPayment.objects.get(pk=pk)
    return render(request, 'payments/payment_detail.html', {'payment': payment})

@login_required
def wallet_view(request):
    try:
        # Get or create wallet for the user
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        # Get user's transactions
        transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        
        # Get user's bank accounts
        bank_accounts = BankAccount.objects.filter(user=request.user)
        
        context = {
            'wallet': wallet,
            'transactions': transactions,
            'bank_accounts': bank_accounts
        }
        return render(request, 'payments/wallet.html', context)
    except Exception as e:
        messages.error(request, f"Error loading wallet: {str(e)}")
        return redirect('dashboard:dashboard-home')

@login_required
def add_money(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            payment_method = request.POST.get('payment_method')
            
            if amount < 100:
                messages.error(request, "Minimum amount to add is ₹100")
                return redirect('payments:wallet')
            
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
            with transaction.atomic():
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='DEPOSIT',
                    payment_method=payment_method,
                    status='pending'
                )
                
                # Update wallet balance
                wallet.balance += amount
                wallet.save()
                
                # Update transaction status
                transaction_obj.status = 'completed'
                transaction_obj.save()
                
                messages.success(request, f"Successfully added ₹{amount} to your wallet")
                return redirect('payments:wallet')
                
        except Exception as e:
            messages.error(request, f"Error adding money: {str(e)}")
            return redirect('payments:wallet')
    
    return redirect('payments:wallet')

@login_required
def withdraw_money(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            bank_account_id = request.POST.get('bank_account')
            
            if amount < 100:
                messages.error(request, "Minimum amount to withdraw is ₹100")
                return redirect('payments:wallet')
            
            wallet = Wallet.objects.get(user=request.user)
            bank_account = BankAccount.objects.get(id=bank_account_id, user=request.user)
            
            if wallet.balance < amount:
                messages.error(request, "Insufficient balance")
                return redirect('payments:wallet')
            
            with transaction.atomic():
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='WITHDRAWAL',
                    payment_method='BANK_TRANSFER',
                    status='pending',
                    description=f"Withdrawal to {bank_account.bank_name} - {bank_account.account_number}"
                )
                
                # Update wallet balance
                wallet.balance -= amount
                wallet.save()
                
                # Update transaction status
                transaction_obj.status = 'completed'
                transaction_obj.save()
                
                messages.success(request, f"Successfully withdrew ₹{amount} to your bank account")
                return redirect('payments:wallet')
                
        except Exception as e:
            messages.error(request, f"Error withdrawing money: {str(e)}")
            return redirect('payments:wallet')
    
    return redirect('payments:wallet')

@login_required
def transaction_detail(request, pk):
    transaction_obj = get_object_or_404(Transaction, pk=pk, wallet__user=request.user)
    return render(request, 'payments/transaction_detail.html', {'transaction': transaction_obj})

class TransactionHistoryView(LoginRequiredMixin, ListView):
    template_name = 'payments/transaction_history.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        wallet = Wallet.objects.get(user=self.request.user)
        return Transaction.objects.filter(wallet=wallet).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet = Wallet.objects.get(user=self.request.user)
        context['wallet'] = wallet
        
        # Get monthly statistics
        this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_stats = Transaction.objects.filter(
            wallet=wallet,
            created_at__gte=this_month
        ).aggregate(
            income=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
            expenses=Sum('amount', filter=Q(transaction_type='WITHDRAWAL'))
        )
        context['monthly_income'] = monthly_stats['income'] or 0
        context['monthly_expenses'] = monthly_stats['expenses'] or 0
        return context

class AddMoneyView(LoginRequiredMixin, CreateView):
    template_name = 'payments/add_money.html'
    success_url = reverse_lazy('payments:wallet')
    
    def form_valid(self, form):
        form.instance.wallet = Wallet.objects.get(user=self.request.user)
        form.instance.transaction_type = 'credit'
        return super().form_valid(form)

class WithdrawView(LoginRequiredMixin, CreateView):
    template_name = 'payments/withdraw.html'
    success_url = reverse_lazy('payments:wallet')
    
    def form_valid(self, form):
        form.instance.wallet = Wallet.objects.get(user=self.request.user)
        form.instance.transaction_type = 'debit'
        return super().form_valid(form)
