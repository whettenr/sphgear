from decimal import Decimal
from django.conf import settings
from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save

from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponseRedirect

# from localflavor.ca.ca_provinces import PROVINCE_CHOICES
# from localflavor.ca.models import CAProvinceField
# from localflavor.us.us_states import STATE_CHOICES
# from localflavor.us.models import USStateField

from carts.models import Cart
from django.core.validators import ValidationError


import braintree

if settings.DEBUG:
	braintree.Configuration.configure(braintree.Environment.Sandbox,
      merchant_id=settings.BRAINTREE_MERCHANT_ID,
      public_key=settings.BRAINTREE_PUBLIC,
      private_key=settings.BRAINTREE_PRIVATE)



class UserCheckout(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True) #not required
	email = models.EmailField(unique=True) #--> required
	braintree_id = models.CharField(max_length=120, null=True, blank=True)

	def __unicode__(self): #def __str__(self):
		return self.email

	@property
	def get_braintree_id(self,):
		instance = self
		if not instance.braintree_id:
			result = braintree.Customer.create({
			    "email": instance.email,
			})
			if result.is_success:
				instance.braintree_id = result.customer.id
				instance.save()
		return instance.braintree_id

	def get_client_token(self):
		customer_id = self.get_braintree_id
		if customer_id:
			client_token = braintree.ClientToken.generate({
			    "customer_id": customer_id
			})
			return client_token
		return None


def update_braintree_id(sender, instance, *args, **kwargs):
	if not instance.braintree_id:
		instance.get_braintree_id


post_save.connect(update_braintree_id, sender=UserCheckout)



class UserAddress(models.Model):
	user = models.ForeignKey(UserCheckout)
	active = models.BooleanField(default=True)
	street = models.CharField(max_length=120)
	city = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	zipcode = models.CharField(max_length=120)
	

	def __unicode__(self):
		return "%s, %s, %s" %(self.street, self.state, self.country)

	def get_address(self):
		return "%s, %s, %s, %s, %s" %(self.street, self.city, self.state, self.country, self.zipcode)




class Carrier(models.Model):
	name = models.CharField(max_length=120)
	link = models.URLField(null=True, blank=True)

	def __unicode__(self):
		return self.name

class ShippingCost(models.Model):
	name = models.CharField(max_length=120)
	state = models.CharField(max_length=50, null=True, blank=True)
	country = models.CharField(max_length=50, null=True, blank=True)
	weight_from = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
	weight_to = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
	price = models.DecimalField(decimal_places=2, max_digits=5, default=10.00)	

	def __unicode__(self):
		return self.name		

COUPON_CHOICES = (
	('%', '%'),
	('$', '$'),
	('free shipping', 'Free Shipping'),
)

class CouponCode(models.Model):
	name = models.CharField(max_length=12, unique=True)
	status = models.CharField(max_length=15, choices=COUPON_CHOICES, default='$')
	discount_value = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)
	start_date = models.DateField(null=True, blank=True)
	expiration_date = models.DateField(null=True, blank=True)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.name

ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('shipped', 'Shipped'),
	('refunded', 'Refunded'),
)

class Order(models.Model):
	status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
	cart = models.ForeignKey(Cart)
	user = models.ForeignKey(UserCheckout, null=True)
	
	shipping_address = models.ForeignKey(UserAddress, related_name='shipping', null=True)
	shipping_location_cost = models.ForeignKey(ShippingCost, null=True, blank=True)
	shipping_price = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)

	coupon = models.ForeignKey(CouponCode, null=True, blank=True)
	
	order_total = models.DecimalField(max_digits=50, decimal_places=2)
	order_id = models.CharField(max_length=20, null=True, blank=True)
	order_weight = models.DecimalField(max_digits=50, decimal_places=2, default=0.00)
	tracking_number = models.CharField(max_length=120, null=True, blank=True)
	shipping_carrier = models.ForeignKey(Carrier, null=True, blank=True)


	def __unicode__(self):
		return str(self.cart.id)

	class Meta:
		ordering = ['-id']

	def get_absolute_url(self):
		return reverse("order_detail", kwargs={"pk": self.pk})

	def mark_completed(self, order_id=None):
		self.status = "paid"
		if order_id and not self.order_id:
			self.order_id = order_id
		self.save()

	def get_order_weight(self):
		weight = 0 
		for i in self.cart.cartitem_set.all():
			weight += i.quantity * i.item.product.weight
		return weight


def order_pre_save(sender, instance, *args, **kwargs):
	# state = instance.shipping_address.state
	# country = instance.shipping_address.country
	# weight = instance.get_order_weight()
	# shipping_price = 30.00
	# ship_location = ShippingCost.objects.filter(state=state)
	
	# if ship_location == None:
	# 	ship_location = ShippingCost.objects.filter(country=country)
	# if ship_location != None:
	# 	ship_weight = ShippingCost.objects.filter(weight_from__lte=weight, weight_to__gte=weight)
	# 	ship_intersect = ship_weight.filter(pk__in=ship_location)	
	# 	print ship_intersect
	# 	if ship_intersect.count() > 0:
	# 		shipping_price = ship_intersect[0].price
	# 		instance.shipping_location_cost = ship_location[0]
	# print weight
	# print shipping_price
	
	#cart_total = instance.cart.total
	print instance.order_total
	#order_total = Decimal(instance.shipping_price) + Decimal(instance.cart.total)

	# instance.shipping_price = shipping_price
	#instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)

def order_post_save(sender, instance, *args, **kwargs):

	if instance.status == "shipped" or instance.status == "refunded":
		order = instance
		print "shipped!"
		print order.user.email
		template = get_template('orders/order_summary_short.html')
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
		# if instance.status == "refunded":
		# 	print braintree.Transaction.refund(order.order_id)
	

post_save.connect(order_post_save, sender=Order)

	 	