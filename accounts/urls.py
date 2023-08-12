from django.urls import path
from .views import RegisterView, UserView, SubscriptionView
from .views import ProductList, ProductDetail, GetCart
from .views import update_cart, remove_all, add_to_cart, CategoryList, CategoryProductsList, SalesDiscountProducts, RecommendProducts, NewProducts, GetWishlist, CreateCheckoutSessionView, ShippingInformationCreateUpdateView
from . import views

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('user/', UserView.as_view()),
    path('subscription/', SubscriptionView.as_view()),
    path('products/', ProductList.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product_detail'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('cart/', GetCart.as_view(), name='get-cart'),
    path('cart/update/', update_cart, name='update-cart'),
    path('cart/remove-all/', remove_all, name='remove-all'),
    path('categories/', CategoryList.as_view(), name='category_list'),
    path('category/<str:name>/', CategoryProductsList.as_view(), name='category-products'),
    path('sales-products/', SalesDiscountProducts.as_view()),
    path('recommend-products/', RecommendProducts.as_view()),
    path('new-products/', NewProducts.as_view()),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', GetWishlist.as_view(), name='wishlist'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('shipping-information/', ShippingInformationCreateUpdateView.as_view(), name='shipping-information'),




]
