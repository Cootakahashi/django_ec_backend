from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Category
from .models import Cart, CartItem, ShippingInformation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'customer_id', 'current_period_end')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'




class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'


class ShippingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingInformation
        fields = '__all__'