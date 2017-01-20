import braintree
from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
# from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from datetime import date
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context
from django.template.loader import get_template
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin


from orders.forms import GuestCheckoutForm
from orders.forms import CouponForm
from orders.mixins import CartOrderMixin
from orders.models import CouponCode, Order, UserAddress, UserCheckout

from products.models import Variation


from .models import Cart, CartItem




if settings.DEBUG:
	braintree.Configuration.configure(braintree.Environment.Sandbox,
      merchant_id=settings.BRAINTREE_MERCHANT_ID,
      public_key=settings.BRAINTREE_PUBLIC,
      private_key=settings.BRAINTREE_PRIVATE)


def find_user_cart_and_order(self):
	user_carts = Cart.objects.filter(user=self.request.user).order_by('timestamp')
	print user_carts
	if user_carts:
		for cart in user_carts:
			print cart
			orders = cart.order_set.filter(status='created')
			if orders or not cart.order_set.all():
				try:
					self.request.session["order_id"] = orders[0].id
				except:
					pass
				cart_id = cart.id
				print "yo im out"
				return cart_id


class ItemCountView(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			
			cart_id = self.request.session.get("cart_id")
			if cart_id == None:
				if request.user.is_authenticated():
					self.request.session["cart_id"] = cart_id = find_user_cart_and_order(self)
			if cart_id == None:
				count = 0
			else:
				cart = Cart.objects.get(id=cart_id)
				count = cart.total_item
			request.session["cart_item_count"] = count
			print cart_id
			return JsonResponse({"count": count})
		else:
			raise Http404



class CartView(SingleObjectMixin, View):
	model = Cart
	template_name = "carts/view.html"

	def get_object(self, *args, **kwargs):
		self.request.session.set_expiry(0)
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			if self.request.user.is_authenticated():
				cart_id = find_user_cart_and_order(self)
			if cart_id == None:
				print 'yuh'
				cart = Cart()
				cart.tax_percentage = 0.085
				cart.total_item = 0
				
				cart.save()
				cart_id = cart.id
			self.request.session["cart_id"] = cart_id
		cart = Cart.objects.get(id=cart_id)

		if self.request.user.is_authenticated():
			cart.user = self.request.user
			cart.save()

		print cart.id
		print cart.order_set.all()
		return cart

	def get(self, request, *args, **kwargs):
		cart = self.get_object()
		item_id = request.GET.get("item")
		delete_item = request.GET.get("delete", False)
		flash_message = ""
		item_added = False
		if item_id:
			item_instance = get_object_or_404(Variation, id=item_id)
			qty = request.GET.get("qty", 1)
			try:
				if int(qty) < 1:
					delete_item = True
			except:
				raise Http404
			cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
			if created:
				flash_message = "Successfully added to the cart"
				item_added = True
			if delete_item:
				flash_message = "Item removed successfully."
				cart_item.delete()
			else:
				if not created:
					flash_message = "Quantity has been updated successfully."
				cart_item.quantity = qty
				cart_item.save()
			if not request.is_ajax():
				return HttpResponseRedirect(reverse("cart"))
				#return cart_item.cart.get_absolute_url()
		
		if request.is_ajax():
			try:
				total = cart_item.line_item_total
			except:
				total = None
			try:
				subtotal = cart_item.cart.subtotal
			except:
				subtotal = None

			try:
				cart_total = cart_item.cart.total
			except:
				cart_total = None

			try:
				tax_total = cart_item.cart.tax_total
			except:
				tax_total = None

			try:
				total_items = cart_item.cart.items.count()
			except:
				total_items = 0

			data = {
					"deleted": delete_item, 
					"item_added": item_added,
					"line_total": total,
					"subtotal": subtotal,
					"cart_total": cart_total,
					"tax_total": tax_total,
					"flash_message": flash_message,
					"total_items": total_items
					}

			return JsonResponse(data) 


		context = {
			"object": self.get_object()
		}
		template = self.template_name
		return render(request, template, context)




class CheckoutView(CartOrderMixin, FormMixin, DetailView):
	model = Cart
	template_name = "carts/checkout_view.html"
	form_class = GuestCheckoutForm
	coupon_form = CouponForm
	def get_object(self, *args, **kwargs):
		cart = self.get_cart()
		if cart == None:
			return None
		return cart

	def get(self, request, *args, **kwargs):
		get_data = super(CheckoutView, self).get(request, *args, **kwargs)
		cart = self.get_object()
		if cart == None:
			return redirect("cart")
		new_order = self.get_order()
		user_checkout_id = request.session.get("user_checkout_id")
		if user_checkout_id != None:
			print "user_checkout_id != None get"
			user_checkout = UserCheckout.objects.get(id=user_checkout_id)
			new_order.user = user_checkout
			new_order.save()
			if new_order.shipping_address == None:
			 	return redirect("order_address")
			
		return get_data


	def get_context_data(self, *args, **kwargs):
		context = super(CheckoutView, self).get_context_data(*args, **kwargs)
		user_can_continue = False
		user_check_id = self.request.session.get("user_checkout_id")
		if self.request.user.is_authenticated():
			
			user_can_continue = True
			user_checkout, created = UserCheckout.objects.get_or_create(email=self.request.user.email)
			user_checkout.user = self.request.user
			user_checkout.save()
			context["client_token"] = user_checkout.get_client_token()
			self.request.session["user_checkout_id"] = user_checkout.id
		elif not self.request.user.is_authenticated() and user_check_id == None:
			# context["login_form"] = AuthenticationForm()
			context["next_url"] = self.request.build_absolute_uri()
		else:
			pass

		if user_check_id != None:
			print "user_check_id != None: get context"
			user_can_continue = True
			if not self.request.user.is_authenticated(): #GUEST USER
				user_checkout_2 = UserCheckout.objects.get(id=user_check_id)
				context["client_token"] = user_checkout_2.get_client_token()
		
		#if self.get_cart() is not None:
		context["order"] = self.get_order()
		order = self.get_order()
		context["user_can_continue"] = user_can_continue
		context["form"] = self.get_form()
		context["coupon_form"] = self.coupon_form
		return context

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()

		coupon_form = self.coupon_form(request.POST)
		
		if coupon_form.is_valid():
			if '_remove' in self.request.POST:
				# print "hi"
				order = self.get_order()
				if order.coupon:
					order.coupon = None
					messages.success(self.request, "Coupon code was removed!")
					order.save()
				else:
					messages.error(self.request, "No coupon to be removed from order")

			elif '_coupon' in self.request.POST:
				code = coupon_form.cleaned_data['coupon_code']
				try:
					check = CouponCode.objects.get(name=code)
				except:
					check = None
				if check == None:
					messages.error(self.request, "Coupon Code was not found")
				else:
					order = self.get_order()
					if order.coupon:
						messages.error(self.request, "A coupon has already been applied to this order. Remove coupon first to use another")
					else:
						if check.start_date > date.today():
							messages.error(self.request, "This coupon code has not been inititated yet. Contact us for more info.")
						elif check.expiration_date < date.today():
							messages.error(self.request, "This coupon code has been expired.")
						elif not check.active:
							messages.error(self.request, "This coupon code has not been activated.")
						else:
							order.coupon = check
							messages.success(self.request, "Coupon code " + check.name + " was applied!")
							if order.coupon.status == '%':
								order.order_total = order.order_total - order.cart.total*(order.coupon.discount_value/100)
							elif order.coupon.status == '$':
								order.order_total = order.order_total - order.coupon.discount_value
							elif order.coupon.status == 'free shipping':
								order.order_total = order.order_total - order.shipping_price
								order.shipping_price = 0.00
							order.save()



		if form.is_valid():
			email = form.cleaned_data.get("email")
			user_checkout, created = UserCheckout.objects.get_or_create(email=email)
			request.session["user_checkout_id"] = user_checkout.id
			return self.form_valid(form)
		else:
			return self.form_invalid(form)
		

	def get_success_url(self):
		return reverse("checkout")






class CheckoutFinalView(CartOrderMixin, View):
	def post(self, request, *args, **kwargs):

		order = self.get_order()
		order_total = order.order_total
		print "order total"
		print order_total
		print "im printing"
		if '_remove' in self.request.POST:
			print 'hi'
		nonce = request.POST.get("payment_method_nonce")
		if nonce:
			result = braintree.Transaction.sale({
			    "amount": order_total,
			    "payment_method_nonce": nonce,
			    "shipping": {
				    "postal_code": "%s" %(order.shipping_address.zipcode),
				    
				 },
			    "options": {
			        "submit_for_settlement": True
			    }
			})

			if result.is_success:
				# result.transaction.id to order
				print order.user.email
				template = get_template('orders/order_view_email.html')
				context = Context({
					'order': order,
				})
				content = template.render(context)

				email = EmailMessage(
					order.user.email +"'s Order Summary",
					content,
					settings.EMAIL_MAIN,
					[order.user.email, 'rmw95@txstate.edu'],
					#['sphperformancegear@gmail.com', 'kyle.schurig@gmail.com', 'whettenrmw@gmail.com'],	
				)
				email.content_subtype = "html"
				email.send()
				messages.success(request, 'Email sent!')


				order.mark_completed(order_id=result.transaction.id)
				messages.success(request, "Thank you for your order.")
				del request.session["cart_id"]
				del request.session["order_id"]
			else:
				#messages.success(request, "There was a problem with your order.")
				messages.success(request, "%s" %(result.message))
				return redirect("checkout")

		return redirect("order_detail", pk=order.pk)

	def get(self, request, *args, **kwargs):
		return redirect("checkout")



