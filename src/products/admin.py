from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget

from .models import Product, Variation, ProductImage, Category

# class ProductVariationImageInline(admin.TabularInline):
# 	model = ProductVariationImage
# 	extra = 0
# 	max_num = 10

class VariationInline(admin.TabularInline):
	model = Variation
	extra = 0
	max_num = 10

class ProductImageAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'product_var']
	list_filter = ['product_var']


class ProductAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'weight','default']
	list_editable = ['default']
	list_filter = ['default']


	inlines = [
		VariationInline,
	]
	formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget },
    }
	class Meta:
		model = Product

admin.site.register(Product, ProductAdmin)

#admin.site.register(Variation)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Category)
