from django.contrib import admin
from .models import Product, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'price', 'stock', 'image')
    formfield_overrides = {}


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