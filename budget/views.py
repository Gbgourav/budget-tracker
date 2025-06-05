from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Category, Transaction, Budget
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  # Add this line
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()  # Add this line
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['category__name', 'description']
    ordering_fields = ['amount', 'date']

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        category = self.request.query_params.get('category')
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if category:
            queryset = queryset.filter(category__id=category)
        if amount_min:
            queryset = queryset.filter(amount__gte=amount_min)
        if amount_max:
            queryset = queryset.filter(amount__lte=amount_max)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()  # Add this line
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        month = request.query_params.get('month', timezone.now().strftime('%Y-%m-01'))
        month_date = datetime.strptime(month, '%Y-%m-%d').date()
        
        total_income = Transaction.objects.filter(
            user=request.user, transaction_type='income', date__year=month_date.year, date__month=month_date.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_expenses = Transaction.objects.filter(
            user=request.user, transaction_type='expense', date__year=month_date.year, date__month=month_date.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        budget = Budget.objects.filter(user=request.user, month__year=month_date.year, month__month=month_date.month).first()
        budget_amount = budget.amount if budget else 0
        
        return Response({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': total_income - total_expenses,
            'budget': budget_amount,
            'budget_remaining': budget_amount - total_expenses if budget_amount else 0
        })
