from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Product, Cart, CartItem, Category, UserAccount, WishlistItem, ShippingInformation
# from django.contrib.auth.models import UserAccount
from .serializers import UserSerializer, CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, ShippingInformationSerializer
from django.shortcuts import get_object_or_404
User = get_user_model()
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import render, redirect
from django.http import JsonResponse
import stripe
from django.conf import settings

# アカウント登録
class RegisterView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        try:
            data = request.data
            name = data['name']
            email = data['email'].lower()
            password = data['password']

            # ユーザーの存在確認
            if not User.objects.filter(email=email).exists():
                # ユーザーが存在しない場合は作成
                User.objects.create_user(name=name, email=email, password=password)

                return Response(
                    {'success': 'ユーザーの作成に成功しました'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': '既に登録されているメールアドレスです'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except:
            return Response(
                {'error': 'アカウント登録時に問題が発生しました'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ユーザー情報取得
class UserView(APIView):
    def get(self, request):
        try:
            user = request.user
            user = UserSerializer(user)

            return Response(
                {'user': user.data},
                status=status.HTTP_200_OK
            )
        
        except:
            return Response(
                {'error': 'ユーザーの取得に問題が発生しました'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# サブスク定期請求
class SubscriptionView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            print("SubscriptionView")
            print(request.data)
            email = request.data["email"]
            customer_id = request.data["customer_id"]
            created = request.data["created"]
            user_data = User.objects.filter(customer_id=customer_id)
            if len(user_data):
                user_data = user_data[0]
            else:
                user_data = User.objects.get(email=email)
                user_data.customer_id = customer_id
            created = datetime.fromtimestamp(created)
            # 有効期限は1ヶ月後を設定
            user_data.current_period_end = created + relativedelta(months=1)
            user_data.save()

            return Response(
                {'success': 'サブスク有効期限の更新に成功しました'},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {'error': 'サブスク有効期限の更新に失敗しました'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
def add_to_cart(request):
    try:
        user = UserAccount.objects.get(id=request.user.id)
    except Exception as e:
        print("======ERROR======")
        print(e)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)  # エラーレスポンスを返す

    product_id = request.data['product_id']
    product = Product.objects.get(id=product_id)

    # カートの取得または作成
    cart, created = Cart.objects.get_or_create(user=user, defaults={'user': user})
    
    # カートアイテムの作成
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'cart': cart, 'product': product})

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return Response({"message": "Product added to cartda!!!"}, status=status.HTTP_201_CREATED)

class GetCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        print(cart)
        items = CartItem.objects.filter(cart=cart)
        cart_data = [
            {
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": item.product.price,
                },
                "quantity": item.quantity,
                "total_price": item.get_total_price(),
                "image_url": item.product.image.url if item.product.image else 'photos/default.jpg'
            }
            for item in items
        ]

        return Response({"items": cart_data}, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def update_cart(request):
    user = UserAccount.objects.get(id=request.user.id)
    product_id = request.data['product_id']
    action = request.data['action']
    product = Product.objects.get(id=product_id)
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    elif action == "remove":
        cart_item.delete()
        return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

    cart_item.save()
    return Response({"message": "Cart updated"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def remove_all(request):
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    print(cart)
    cart.items.all().delete()
    return Response({"message": "All items removed from cart"}, status=status.HTTP_200_OK)






class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = []
    permission_classes = []

class CategoryProductsList(generics.ListAPIView):
    serializer_class = ProductSerializer

    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        category_name = self.kwargs['name']
        category = get_object_or_404(Category, name=category_name)
        return Product.objects.filter(category=category)
    

class SalesDiscountProducts(generics.ListAPIView):
    queryset = Product.objects.filter(sales_discount=True)
    serializer_class = ProductSerializer
    authentication_classes = []
    permission_classes = []

class RecommendProducts(generics.ListAPIView):
    queryset = Product.objects.filter(recommend=True)
    serializer_class = ProductSerializer
    authentication_classes = []
    permission_classes = []

class NewProducts(generics.ListAPIView):
    queryset = Product.objects.filter(new_product=True)
    serializer_class = ProductSerializer
    authentication_classes = []
    permission_classes = []


class GetWishlist(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("GET WISHLIST")
        
        wishlist_items = WishlistItem.objects.filter(user=request.user)
        wishlist_data = [{"product_id": item.product.id} for item in wishlist_items]
        
        return Response(wishlist_data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    WishlistItem.objects.create(user=request.user, product=product)
    print("added to wishlist")
    print(request.user)
    print(product_id)
    print(product)
    return Response({"status": "success", "message": "Product added to wishlist"})

@api_view(['POST'])
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    print("remove from wishlist")
    try:
        item = WishlistItem.objects.get(user=request.user, product=product)
        print(item)
        item.delete()
        return Response({"status": "success", "message": "Product removed from wishlist"})
    except WishlistItem.DoesNotExist:
        return Response({"status": "error", "message": "Product not found in wishlist"}, status=status.HTTP_404_NOT_FOUND)
    


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    print("CreateCheckoutSessionView")
    def post(self, request, *args, **kwargs):
        print(request.data) # Debug statement

        amount = request.data.get('totalPrice', 0) * 100 # Cents
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Total',
                            },
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/success'),
                cancel_url=request.build_absolute_uri('/cancel'),
            )
            return Response({'id': session.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        




class ShippingInformationCreateUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ShippingInformation.objects.all()
    serializer_class = ShippingInformationSerializer
    lookup_field = 'user'  # UserとのOneToOneリレーションを使用するための設定

    def get_object(self):
        # 既存のShippingInformationを取得するか、新しいインスタンスを作成
        obj, created = ShippingInformation.objects.get_or_create(user=self.request.user)
        return obj