from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic.edit import FormMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.detail import DetailView
from  django.views.generic.list import ListView

from .forms import AddressForm, UserAddressForm
from .mixins import CartOrderMixin, LoginRequiredMixin
from .models import UserAddress, UserCheckout, Order

# view of individual order
class OrderDetail(DetailView):
	model = Order

	def dispatch(self, request, *args, **kwargs):
		try:
			user_check_id = self.request.session.get("user_checkout_id")
			user_checkout = UserCheckout.objects.get(id=user_check_id)
		except UserCheckout.DoesNotExist:
			user_checkout = UserCheckout.objects.get(user=request.user)
		except:
			user_checkout = None

		obj = self.get_object()
		if obj.user == user_checkout and user_checkout is not None:
			return super(OrderDetail, self).dispatch(request, *args, **kwargs)
		else:
			raise Http404

# view of all orders associated with a registered user
class OrderList(LoginRequiredMixin, ListView):
	queryset = Order.objects.all()
	template_name = "orders/order_list.html"
	def get_queryset(self):
		user_check_id = self.request.user.id
		try:
			user_checkout = UserCheckout.objects.get(id=user_check_id)
			return super(OrderList, self).get_queryset().filter(user=user_checkout)
		except:
			user_checkout=None
			return None

# view to create address
class UserAddressCreateView(CreateView):
	form_class = UserAddressForm
	template_name = "address_form.html"
	success_url = "/checkout/address/"

	def get_checkout_user(self):
		user_check_id = self.request.session.get("user_checkout_id")
		user_checkout = UserCheckout.objects.get(id=user_check_id)
		return user_checkout

	def form_valid(self, form, *args, **kwargs):
		print 'out here'
		form.instance.user = self.get_checkout_user()
		print 'out here'
		if self.request.POST:
			print "howdy"	
		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

# class UserAddressUpdateView(UpdateView):
#     model = UserAddress
#     form_class = UserAddressForm
#     template_name = "forms.html"
#     success_url = "/checkout/address/"

# view for displaying and choosing address associated with paticular user
class AddressSelectFormView(CartOrderMixin, FormView):
	form_class = AddressForm
	template_name = "orders/address_select.html"

	def dispatch(self, *args, **kwargs):
		s_address = self.get_addresses()
		if s_address.count() == 0:
			messages.success(self.request, "Please add a shipping address before continuing")
			return redirect("user_address_create")
		else:
			return super(AddressSelectFormView, self).dispatch(*args, **kwargs)


	def get_addresses(self, *args, **kwargs):
		user_check_id = self.request.session.get("user_checkout_id")
		user_checkout = UserCheckout.objects.get(id=user_check_id)
		s_address = UserAddress.objects.filter(
				user=user_checkout,
				active = True
			)
		return s_address

		
	def get_form(self, *args, **kwargs):
		form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
		s_address = self.get_addresses()
		form.fields["shipping_address"].queryset = s_address
		return form

	def form_valid(self, form, *args, **kwargs):
		shipping_address = form.cleaned_data["shipping_address"]
		
		if '_select' in self.request.POST:
			if  shipping_address == None:
				messages.error(self.request, "Please select shipping address to continue")
				return redirect("/checkout/address/")
		if '_remove' in self.request.POST:
			if shipping_address:
				address = UserAddress.objects.get(id=shipping_address.id)
				print address
				print address.active
				address.active = False
				address.save()
				print address
				print address.active

				return redirect("/checkout/address/")
			else:
				messages.error(self.request, "Please select shipping address to remove")
		# if '_edit' in self.request.POST:
		# 	if shipping_address:
		# 		return redirect("/checkout/address/edit/" + str(shipping_address.pk))

		# 	UserAddress.objects.get(id=billing_address.id).delete()
		#	UserAddress.objects.get(id=billing.id).delete()
		order = self.get_order()
		order.shipping_address = shipping_address
		order.save()
		return  super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

	def get_success_url(self, *args, **kwargs):
		return 	"/checkout/"
