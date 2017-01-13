from django.contrib import admin

# Register your models here.

from .forms import CouponAdminForm
from .models import UserCheckout, UserAddress, Order, ShippingCost, CouponCode, Carrier


class OrderAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', "status", "shipping_address", "shipping_price", "coupon"]
	list_editable = ["status"]
	list_filter = ["status", "shipping_address", "coupon"]

	

	search_fields = ["title", "content", "coupon"]
	class Meta:
		model = Order

class CouponCodeAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', "status", "discount_value", 'start_date', 'expiration_date', 'active']
	list_editable = ["active"]

	form = CouponAdminForm

admin.site.register(UserCheckout)
admin.site.register(UserAddress)
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingCost)
admin.site.register(Carrier)
admin.site.register(CouponCode, CouponCodeAdmin)