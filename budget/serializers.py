from rest_framework import serializers
from .models import Category, Transaction, Budget
from django.utils import timezone

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'category', 'category_name', 'amount', 'transaction_type', 'description', 'date', 'created_at']

    def validate(self, data):
        if data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return data

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'amount', 'month', 'created_at']

    def validate_month(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Budget cannot be set for a future month.")
        return value