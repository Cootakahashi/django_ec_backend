from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Category, Product, WishlistItem, ShippingInformation

User = get_user_model()

admin.site.register(User)
admin.site.register(WishlistItem)
admin.site.register(ShippingInformation)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'price', 'in_stock', 'is_active']
    list_editable = ['price', 'in_stock', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    


from .models import Cart, CartItem
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_names','created_at', 'get_total_items', 'get_total_price']
    inlines = [CartItemInline]  # インライン表示の追加

    def get_total_items(self, obj):
        return obj.items.count()

    def get_total_price(self, obj):
        total_price = sum(item.get_total_price() for item in obj.items.all())
        return f"${total_price:.2f}"
    
    def product_names(self, obj):
        return ", ".join(item.product.name for item in obj.items.all())
    
    get_total_items.short_description = 'Total Items'
    get_total_price.short_description = 'Total Price'
    product_names.short_description = 'Product Names'



@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'get_total_price']

    def get_total_price(self, obj):
        return f"${obj.get_total_price():.2f}"

    get_total_price.short_description = 'Total Price'

