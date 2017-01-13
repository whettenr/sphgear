from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator


class CompanyInfo(models.Model):
	email = models.EmailField()
	bio = models.TextField()
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=16) # validators should be a list 
	fb_link = models.URLField(null=True, blank=True) 
	insta_link = models.URLField(null=True, blank=True) 

	def __unicode__(self):
		return self.email