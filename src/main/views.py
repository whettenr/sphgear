from django.conf import settings

from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import redirect
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render

from products.models import ProductFeatured, Product
from posts.models import Post
from .models import CompanyInfo
from .forms import ContactForm

# Create your views here.
def home(request):
	featured_images = ProductFeatured.objects.filter(active=True).order_by("?")	
	count = featured_images.count()
	posts = Post.objects.active()[:6]
	if request.user.is_staff or request.user.is_superuser:
		posts = Post.objects.all()[:6]
	products = Product.objects.all().order_by("?")[:6]
	
	context = {
		"count":count,
		"featured_images":featured_images,
		"posts":posts,
		"products":products
	}
	return render(request, "home.html", context)

def contact(request):
	company_info = CompanyInfo.objects.first()
	form = ContactForm
	if request.method == 'POST':
		form = form(data=request.POST)

		if form.is_valid():
			contact_name = request.POST.get(
				'contact_name'
			, '')
			contact_email = request.POST.get(
				'contact_email'
			, '')
			form_content = request.POST.get('content', '')

			# Email the profile with the 
			# contact information
			template = get_template('contact_template.txt')
			context = Context({
				'contact_name': contact_name,
				'contact_email': contact_email,
				'form_content': form_content,
			})
			content = template.render(context)

			email = EmailMessage(
				"New contact form submission",
				content,
				settings.EMAIL_MAIN,
				['whettenrmw@gmail.com', 'rmw95@txstate.edu'],
				#['sphperformancegear@gmail.com', 'kyle.schurig@gmail.com', 'whettenrmw@gmail.com'],
				headers = {'Reply-To': contact_email }
			)
			email.send()
			messages.success(request, 'Email sent!')
			return redirect('contact')

	return render(request, 'contact.html', {
		'company_info': company_info,
		'form': form,
    })

def about(request):
	return render(request, "about.html", {})
















