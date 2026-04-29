import copy
from django.contrib import admin
from .models import Product, ProductVariant, ProductVariantImage, Order, OrderItem


class ProductVariantImageInline(admin.TabularInline):
    model = ProductVariantImage
    extra = 1
    fields = ('img', 'order')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'price', 'stock', 'image')
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form = copy.deepcopy(formset.form)

        # Determine category from saved object or from POST data (new product)
        if obj:
            category = obj.category
        else:
            category = request.POST.get('category', '')

        if category == 'shoes':
            formset.form.base_fields['size'].choices = ProductVariant.SHOE_SIZES
        else:
            formset.form.base_fields['size'].choices = ProductVariant.CLOTHING_SIZES
        return formset


class NoExtraButtonsMixin:
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().add_view(request, form_url, extra_context=extra_context)


@admin.register(Product)
class ProductAdmin(NoExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('title', 'category', 'gender', 'variant_count', 'min_price')
    list_filter = ('category', 'gender')
    search_fields = ('title',)
    fields = ('title', 'description', 'material', 'category', 'gender')
    inlines = [ProductVariantInline]

    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Варіацій'

    def min_price(self, obj):
        v = obj.variants.order_by('price').first()
        return f"{v.price} грн" if v else '—'
    min_price.short_description = 'Мін. ціна'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display  = ('product', 'color', 'size', 'price', 'stock')
    list_filter   = ('product', 'color')
    search_fields = ('product__title', 'color')
    inlines       = [ProductVariantImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('title', 'size', 'color', 'price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'email', 'phone', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'payment')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'total_price')
    inlines = [OrderItemInline]