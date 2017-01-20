from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.db.models import Min
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.utils.text import slugify

# Create your models here.

class ProductQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)


class ProductManager(models.Manager):
	def get_queryset(self):
		return ProductQuerySet(self.model, using=self._db)

	def all(self, *args, **kwargs):
		return self.get_queryset().active()

	def get_related(self, instance):
		products_one = self.get_queryset().filter(categories__in=instance.categories.all())
		products_two = self.get_queryset().filter(default=instance.default)
		qs = (products_one | products_two).exclude(id=instance.id).distinct()
		return qs


class Product(models.Model):
	title = models.CharField(max_length=120, unique=True)
	description = models.TextField(blank=True, null=True)
	active = models.BooleanField(default=True)
	categories = models.ManyToManyField('Category', blank=True)
	default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)
	weight = models.DecimalField(decimal_places=2, max_digits=20)
	
	objects = ProductManager()

	class Meta:
		ordering = ["-title"]

	def __unicode__(self): #def __str__(self):
		return self.title 

	def get_absolute_url(self):
		return reverse("product_detail", kwargs={"pk": self.pk})

	def get_image_url(self):

		try:
			img = self.productfeaturedimage_set.first()
		except:
			pass
		if not img:
			var_set = self.variation_set.last()
			img = self.variation_set.last().productimage_set.first()

		if img:
			return img.image.url
		return img

	def get_image_set(self):
		var_set = self.variation_set.all()
		img_set = []
		for var in var_set:
			img_set += var.productimage_set.all()
			print img_set
		for img in img_set:
			print img.image.url
			print img.product_var
		return img_set #None

	def get_min_price(self):
		var_set = self.variation_set.all()
		min_price = var_set.aggregate(Min('price'))
		min_sale = var_set.aggregate(Min('sale_price'))
		if min_price['price__min'] < min_sale['sale_price__min']:
			return var_set.get(price=min_price['price__min']).get_html_price()
		else:
			return var_set.get(sale_price=min_sale['sale_price__min']).get_html_price()






class Variation(models.Model):
	product = models.ForeignKey(Product)
	size = models.CharField(max_length=120)
	color = models.CharField(max_length=120)
	price = models.DecimalField(decimal_places=2, max_digits=20)
	sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
	active = models.BooleanField(default=True)
	inventory = models.IntegerField(null=True, blank=True) #refer none == unlimited amount


	def __unicode__(self):
		return self.get_title()

	def get_price(self):
		if self.sale_price is not None:
			return self.sale_price
		else:
			return self.price

	def get_html_price(self):
		if self.sale_price is not None:
			html_text = "<span class='sale-price'>%s</span> <span class='og-price'>%s</span>" %(self.sale_price, self.price)
		else:
			html_text = "<span class='price'>%s</span>" %(self.price)
		return mark_safe(html_text)

	def get_absolute_url(self):
		return self.product.get_absolute_url()

	def add_to_cart(self):
		return "%s?item=%s&qty=1" %(reverse("cart"), self.id)

	def remove_from_cart(self):
		return "%s?item=%s&qty=1&delete=True" %(reverse("cart"), self.id)

	def get_title(self):
		return "%s - %s  -  %s" %(self.product.title, self.size ,self.color )

	class Meta:
		unique_together = ('size', 'color', 'product')


def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
	product = instance
	variations = product.variation_set.all()
	if variations.count() == 0:
		new_var = Variation()
		new_var.product = product
		new_var.title = "Default"
		new_var.size = "Default"
		new_var.color = "Default"
		new_var.price = 0.00
		new_var.save()


post_save.connect(product_post_saved_receiver, sender=Product)


def image_upload_to(instance, filename):
	title = instance.name + instance.product_var.get_title()
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s.%s" %(slug, file_extension)
	return "products/%s/%s" %(slug, new_filename)


class ProductImage(models.Model):
	name = models.CharField(max_length=120)
	product_var = models.ForeignKey(Variation)
	image = models.ImageField(upload_to=image_upload_to)

	def __unicode__(self):
		return self.name


# Product Category


class Category(models.Model):
	title = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(unique=True)
	description = models.TextField(null=True, blank=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.title


	def get_absolute_url(self):
		return reverse("category_detail", kwargs={"slug": self.slug })



def image_upload_to_featured(instance, filename):
	title = instance.title
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extension)
	return "products/%s/featured/%s" %(slug, new_filename)




class ProductFeaturedImage(models.Model):
	product = models.ForeignKey(Product, null=True, blank=True)
	image = models.ImageField(upload_to=image_upload_to_featured)
	title = models.CharField(max_length=120, unique=True)
	text = models.CharField(max_length=220, null=True, blank=True)
	text_right = models.BooleanField(default=False)
	text_css_color = models.CharField(max_length=6, null=True, blank=True)
	make_image_background = models.BooleanField(default=False)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title

