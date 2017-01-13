from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from carts.models import Cart
from .models import Order
from .models import ShippingCost


class LoginRequiredMixin(object):
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request,*args, **kwargs)



class CartOrderMixin(object):
	def get_order(self, *args, **kwargs):
		cart = self.get_cart()
		if cart is None:
			return None
		new_order_id = self.request.session.get("order_id")
		if new_order_id is None:		
			new_order = Order.objects.create(cart=cart, order_total=0.00)
			new_order.cart = cart
			self.find_shipping_info(new_order)
			order_total = Decimal(new_order.shipping_price) + new_order.cart.total
			new_order.save()
			self.request.session["order_id"] = new_order.id
		else:
			new_order = Order.objects.get(id=new_order_id)
			if not new_order.coupon:
				self.find_shipping_info(new_order)
				new_order.order_total = Decimal(new_order.shipping_price) + new_order.cart.total 
				new_order.save()
		return new_order

	def get_cart(self, *args, **kwargs):
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			return None
		cart = Cart.objects.get(id=cart_id)
		if cart.items.count() <= 0:
			return None
		return cart

	def find_shipping_info(self, order, *args, **kwargs):
		if order.shipping_address:
			state = order.shipping_address.state
			country = order.shipping_address.country
			weight = order.get_order_weight()
			try:
				shipping_price = ShippingCost.objects.get(name="default").price
			except:
				shipping_price = 30.00
			ship_location = ShippingCost.objects.filter(state=state)
			if ship_location == None:
				ship_location = ShippingCost.objects.filter(country=country)
			if ship_location != None:
				ship_weight = ShippingCost.objects.filter(weight_from__lte=weight, weight_to__gte=weight)
				ship_intersect = ship_weight.filter(pk__in=ship_location)	
				if ship_intersect.count() > 0:
					shipping_price = ship_intersect[0].price
					order.shipping_location_cost = ship_location[0]
			order.shipping_price = shipping_price
			order.order_weight = weight
			print shipping_price
			print weight
			print order.order_weight
			print "about to return"
