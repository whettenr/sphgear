from django import forms
import datetime
from pagedown.widgets import PagedownWidget
from django.forms.extras.widgets import SelectDateWidget
from .models import Post


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))
    publish = forms.DateField(widget=forms.SelectDateWidget)
    class Meta:
        model = Post
        fields = [
			"title",
			"content",
			"image",
			"draft",
			"publish",
		]