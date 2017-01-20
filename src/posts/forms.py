from django import forms
import datetime
from pagedown.widgets import PagedownWidget
from django.forms.widgets import SelectDateWidget
from .models import Post
from django.contrib.admin.widgets import AdminDateWidget

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))
    publish = forms.DateField(widget=SelectDateWidget(empty_label=("Choose Year", "Choose Month", "Choose Day"),
    ),)
    class Meta:
		model = Post
		fields = [
			"title",
			"slug",
			"content",
			"image",
			"draft",
			"publish",
		]