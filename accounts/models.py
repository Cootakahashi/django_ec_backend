from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.urls import reverse
from enum import Enum


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email')
        
        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email=email,
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("メールアドレス", max_length=255, unique=True)
    name = models.CharField("名前", max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    customer_id = models.CharField("顧客ID", max_length=255, blank=True, null=True)
    current_period_end = models.DateTimeField("有効期限", blank=True, null=True)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    


class Category(models.Model):
    name = models.CharField("カテゴリ名", max_length=200, unique=True)
    slug = models.SlugField("スラッグ", max_length=200, unique=True)

    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])
    

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField("商品名", max_length=200, unique=True)
    slug = models.SlugField("スラッグ", max_length=200, unique=True)
    image = models.ImageField(upload_to='photos/products', default='photos/default.jpg')
    description = models.TextField("商品説明", max_length=500, blank=True)
    price = models.DecimalField("価格", max_digits=10, decimal_places=2)
    in_stock = models.BooleanField("在庫あり", default=True)
    is_active = models.BooleanField("有効", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    sales_discount = models.BooleanField(default=False) # 割引商品フラグ
    recommend = models.BooleanField(default=False) # 推奨商品フラグ
    new_product = models.BooleanField(default=False) 
    ranking = models.IntegerField(null=True, blank=True) # ランキング

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])
    
class Cart(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart {self.id}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Cart {self.cart.id} Item {self.id}'

    def get_total_price(self):
        return self.product.price * self.quantity
    


class WishlistItem(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)




class ShippingInformation(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)



class Order(models.Model):
    user = models.ForeignKey(UserAccount, related_name='orders', on_delete=models.CASCADE)
    shipping_information = models.ForeignKey(ShippingInformation, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')])
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.name}"
    

class ShippingState(Enum):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELED = 'Canceled'
    
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_state = models.CharField(
        max_length=10,
        choices=[(state.value, state.name) for state in ShippingState],
        default=ShippingState.PENDING.value,
    )