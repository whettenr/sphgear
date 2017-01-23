from __future__ import unicode_literals
from django.db import models
from django.core.validators import RegexValidator
from django.utils.text import slugify

from products.models import Product
from posts.models import Post


class CompanyInfo(models.Model):
	email = models.EmailField()
	bio = models.TextField()
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=16) # validators should be a list 
	fb_link = models.URLField(null=True, blank=True) 
	insta_link = models.URLField(null=True, blank=True) 

	def __unicode__(self):
		return self.email



POSITION_CHOICES = (
	('slide_style_center', 'Center'),
	('slide_style_left', 'Left'),
	('slide_style_right', 'Right'),
)

ANIMATION_CHOICES = (
	('Fade in', (
			('fadeIn', 'Fade In'),
	        ('fadeInLeft', 'Fade in Left'),
	        ('fadeInRight', 'Fade in Right'),
	        ('fadeInUp', 'Fade in Up'),
	        ('fadeInDown', 'Fade in Down'),
	    )
	),
	('Flip in', (
			('flip', 'flip'),
	        ('flipInX', 'Flip in X'),
	        ('flipInY', 'Flip in Y'),
	    )
	),
	('Zoom in',(
			('zoomInUp', 'Zoom In Up'),
			('zoomInDown', 'Zoom In Down'),
			('zoomInLeft', 'Zoom in Left'),
			('zoomInRight', 'Zoom in Right'),
		)
	),
	('lightSpeedIn', 'Light Speed In')
)


def image_upload_to_featured(instance, filename):
	title = instance.title
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s.%s" %(slug, file_extension)
	return "featured/%s/%s" %(slug, new_filename)

class Featured(models.Model):
	product = models.ForeignKey(Product, null=True, blank=True)
	post = models.ForeignKey(Post, null=True, blank=True)
	
	title = models.CharField(max_length=120, unique=True)
	text = models.CharField(max_length=220, null=True, blank=True)
	title_animation = models.CharField(max_length=20, choices=ANIMATION_CHOICES)	
	button_animation = models.CharField(max_length=20, choices=ANIMATION_CHOICES, null=True, blank=True)
	text_animation = models.CharField(max_length=10, choices=ANIMATION_CHOICES, null=True, blank=True)	
	
	image = models.ImageField(upload_to=image_upload_to_featured)


	position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='left')
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title