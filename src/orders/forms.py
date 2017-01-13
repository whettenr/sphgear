from django import forms
from django.contrib.auth import get_user_model

from .models import UserAddress, CouponCode


User = get_user_model()

class GuestCheckoutForm(forms.Form):
	email = forms.EmailField()
	email2 = forms.EmailField(label='Verify Email')

	def clean_email2(self):
		email = self.cleaned_data.get("email")
		email2 = self.cleaned_data.get("email2")

		if email == email2:
			user_exists = User.objects.filter(email=email).count()
			if user_exists != 0:
				raise forms.ValidationError("This User already exists. Please login instead.")
			return email2
		else:
			raise forms.ValidationError("Please confirm emails are the same")

class AddressForm(forms.Form):
	shipping_address = forms.ModelChoiceField(
		queryset=UserAddress.objects.filter(active=True),
		widget = forms.RadioSelect,
		required=False,
		empty_label = None,
		)

class UserAddressForm(forms.ModelForm):
	class Meta:
		model = UserAddress
		fields = [
			'street',
			'city',
			'country',
			'state',
			'zipcode',
		]
		widgets = {'country': forms.HiddenInput(), 'state': forms.HiddenInput()}

class CouponForm(forms.Form):
    coupon_code = forms.CharField(label='Enter Coupon Code', max_length=12, required=False)

# class CouponForm(forms.ModelForm):
# 	class Meta:
# 		model = CouponCode
# 		fields = [
# 			'name'
# 		]


class CouponAdminForm(forms.ModelForm):
	class Meta:
		model = CouponCode
		fields = '__all__'
	
	def clean(self):
		cleaned_data = super(CouponAdminForm, self).clean()
		start_date = self.cleaned_data.get('start_date')
		expiration_date = self.cleaned_data.get('expiration_date')
		status  = self.cleaned_data.get('status')
		discount_value  = self.cleaned_data.get('discount_value')
		if status == '$' or status == '%':
			if not discount_value:
				raise forms.ValidationError("Please enter discount value")
				
		if start_date > expiration_date:
			# msg = u"End date should be greater than start date."
			raise forms.ValidationError("Expiration date should be greater than start date")

			# self._errors["expiration_date"] = form.error_class([msg])
