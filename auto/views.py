import uuid

from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, ListView
from urllib.parse import urlparse

from auto.filters import ProductFilter
from auto.forms import *
from auto.models import *
from autolux import settings
import json
import stripe
from django.utils import timezone
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.http import JsonResponse, BadHeaderError, HttpResponse

signUpForm = SignUpForm()
signInForm = SignInForm()
all_cars = CarCompany.objects.all()
product_list = Product.objects.all()
params = {'signUp': signUpForm, 'signIn': signInForm, "all_cars": all_cars}


class Index(TemplateView):
    template_name = 'index.html'
    all_products = []

    def get(self, request, *args, **kwargs):
        product_filter = ProductFilter(request.GET, queryset=product_list)
        silder_images = SliderImage.objects.all()

        categories = Category_CHOICES

        for category in categories:
            self.all_products += Product.objects.filter(product_category=category[0]).order_by('-created_at')[0:4]
            # self.all_products = self.all_products + list(products)

        home_categories_images = HomePageCategoriesImages.objects.latest()

        params['all_products'] = self.all_products
        params['stripe_key'] = settings.STRIPE_PUBLIC_KEY
        params['filter'] = product_filter
        params['slider_images'] = silder_images
        params['home_categories_images'] = home_categories_images
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        signUpForm = SignUpForm(request.POST)
        if signUpForm.is_valid():
            signUpForm.save()
            email = signUpForm.cleaned_data.get('email')
            raw_password = signUpForm.cleaned_data.get('password1')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            return redirect('index')

        return render(request, self.template_name)


class Products(ListView):
    model = Product
    template_name = 'products.html'
    paginate_by = 12
    product_filter = None

    def get_queryset(self):
        item_name = self.kwargs.get('item_name')
        categoryFilter = self.request.GET.get('product_category')
        sort_by = 'created_at'

        if item_name == 'filterbycar':
            car_make = self.request.GET.get('make')
            car_year = self.request.GET.get('year')
            car_model = self.request.GET.get('model')
            context = Product.objects.filter(cars_related_name__car_year=car_year.strip(),
                                           cars_related_name__model__car_model=car_model.strip(),
                                           cars_related_name__model__company__car_make=car_make.strip())
        elif item_name != "SearchResults" and (categoryFilter == None or categoryFilter == ''):
            context = Product.objects.filter(product_category__iexact=item_name).order_by(sort_by)
        else:
            context = super(Products, self).get_queryset()

        self.product_filter = ProductFilter(self.request.GET, queryset=context)
        context = self.product_filter.qs

        return context

    def get_context_data(self, **kwargs):
        context = super(Products, self).get_context_data(**kwargs)
        item_name = self.kwargs.get('item_name')
        searchTerm = self.request.GET.get('product_title')

        context['foundNothing'] = False
        context['category_wise_images'] = CategoryWiseImageBackground.objects.latest()
        context['item_category'] = item_name
        context['searchTerm'] = searchTerm
        context['filter'] = self.product_filter

        if item_name == "SearchResults":
            context['page_title'] = "Search Results"
        elif item_name == "Suvs":
            context['page_title'] = "4x4/SUV items"
        elif item_name == 'Utilites':
            context['page_title'] = "Outdoor Utilities"
        elif item_name == 'filterbycar':
            context['page_title'] = 'Filter By Car'
        else:
            context['page_title'] = item_name

        # context['price_min_val'] = str(self.product_filter.form.cleaned_data.get('product_price').start)
        # context['price_min_val'] = str(self.product_filter.form.cleaned_data.get('product_price').stop)

        return context


class ProductDescription(TemplateView):
    template_name = 'product_description.html'

    def get(self, request, *args, **kwargs):
        product_filter = ProductFilter(request.GET, queryset=product_list)
        params['filter'] = product_filter

        item_id = kwargs.get('id')
        selected_item = ProductSpecification.objects.filter(product_id_id=item_id)
        productColors = selected_item.first().product_id.product_colors.all()
        new_arrivals = Product.objects.all().order_by('-id')[:4]
        category_wise_images = CategoryWiseImageBackground.objects.latest()
        product_category = selected_item.first().product_id.product_category
        backgroundImage = ''

        if product_category == 'Exterior':
            backgroundImage = category_wise_images.exterior.url
        elif product_category == 'Interior':
            backgroundImage = category_wise_images.interior.url
        elif product_category == 'Mats':
            backgroundImage = category_wise_images.mats.url
        elif product_category == 'Detailing':
            backgroundImage = category_wise_images.car_detailing.url
        elif product_category == 'Leds':
            backgroundImage = category_wise_images.led_lights.url
        elif product_category == 'Suvs':
            backgroundImage = category_wise_images.suv_items.url
        elif product_category == 'Utilites':
            backgroundImage = category_wise_images.outdoor_utilities.url
        else:
            backgroundImage = category_wise_images.others.url

        params['backgroundImage'] = backgroundImage
        params['productColors'] = productColors
        params['item'] = selected_item.first()
        params['new_arrivals'] = new_arrivals
        return render(request, self.template_name,params)


class Contact(TemplateView):
    template_name = 'contact.html'
    def get(self, request, *args, **kwargs):
        product_filter = ProductFilter(request.GET, queryset=product_list)
        params['filter'] = product_filter

        if 'Email' in request.GET:
            subject = request.GET['Subject']
            from_email = request.GET['Email']
            message = request.GET['Message']
            name = request.GET['Name']
            message = "Sender Name: " + name +"\n" + message + "\n" + "From :" + from_email
            try:
                send_mail(subject, message, 'autoluxpk@gmail.com', ['autoluxpk@gmail.com'],
                          fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        return render(request, self.template_name,params)



class About(TemplateView):
    template_name = 'about.html'

    def get(self, request, *args, **kwargs):
        product_filter = ProductFilter(request.GET, queryset=product_list)

        params['filter'] = product_filter
        return render(request, self.template_name,params)


class Login(TemplateView):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)

    def post(self,request,**kwargs):
        signInForm = SignInForm(request.POST)
        if signInForm.is_valid():
            email = signInForm.cleaned_data.get('email')
            raw_password = signInForm.cleaned_data.get('password')
            user = authenticate(username=email, password=raw_password)
            login(request, user)
            return redirect('index')

        return render(request,self.template_name)


class PlaceOrder(TemplateView):
    template_name = 'place_order.html'

    def get(self, request, *args, **kwargs):
        orderForm = UserOrderForm()
        payment_method = "Cash On Delivery"
        token = ""

        if "stripeToken" in request.GET:
            token = request.GET['stripeToken']
            payment_method = "Online Payment"


        orderBackgroundImage = OrderPageBackground.objects.latest()

        args = {
            'orderForm': orderForm,
            'payment_method': payment_method,
            'token':token,
            'orderBackgroundImage': orderBackgroundImage.background_image.url,
            'orderMobileBackgroundImage': orderBackgroundImage.mobile_image.url
        }

        return render(request,self.template_name,args)

    def post(self, request, **kwargs):
        orderForm = UserOrderForm(request.POST)

        if orderForm.is_valid():
            try:
                first_name = orderForm.cleaned_data['first_name']
                last_name = orderForm.cleaned_data['last_name']
                email = orderForm.cleaned_data['email']
                address = orderForm.cleaned_data['address']
                contact_number = orderForm.cleaned_data['contact_number']
                payment_method = request.POST['payment_method']
                token = request.POST['token']

                user = orderForm.save()

                order_number = uuid.uuid4().hex[:6].upper()
                json_order = request.POST['cart_info']
                cart_object = json.loads(json_order)

                colors = ''

                if (len(cart_object['products']) == 0):
                    orderData = {
                        'errors': 'You do not have any items in your cart',
                        'success': False
                    }
                    return JsonResponse(orderData)

                total_bill = 0
                charge = "Stripe Payment id"
                for order in cart_object["products"]:
                    item_count = float(order['price']) * float(order['quantity'])
                    total_bill = total_bill + item_count

                if payment_method == "Online Payment":
                    try:
                        charge = stripe.Charge.create(
                            amount=int(total_bill),
                            currency="usd",
                            source=token,
                            description="The product charged to the user"
                        )
                        # simple.charge_id = charge.id
                    except stripe.error.CardError as ce:
                        return False, ce

                orderProducts = cart_object["products"];
                for order in orderProducts:
                    if 'colors' in order:
                        orderColors = order['colors']
                        for color in orderColors:
                            colors = colors + color + ','
                    else:
                        colors = ''

                    item_count = float(order['price']) * float(order['quantity'])
                    if payment_method == "Online Payment":
                        user.user_without_account = Order(user=user,
                                                          item_id=order['id'],
                                                          item_name=order['name'],
                                                          item_quantity=order['quantity'],
                                                          item_price=order['price'],
                                                          total_price=item_count,
                                                          payment_status=True,
                                                          charge_id = charge.id,
                                                          colors=colors,
                                                          order_number=order_number)
                        # user_order.save()
                        user.user_without_account.save()

                    else:
                        user.user_without_account = Order(user=user,
                                                          item_id=order['id'],
                                                          item_name=order['name'],
                                                          item_quantity=order['quantity'],
                                                          item_price=order['price'],
                                                          total_price=item_count,
                                                          payment_status=False,
                                                          colors=colors,
                                                          order_number=order_number)
                        # direct_order.save()
                        user.user_without_account.save()

                subject = 'New Order Placed'
                message = "Congratulations! New order has been placed " \
                          "with following details. \n\n" \
                          "First Name: " + first_name + " \nLast Name: " + \
                          last_name + "\nEmail: " + email + "\nAddress: " + address + \
                          "\nContact Number: " + contact_number + "\nOrder Number: " + order_number

                send_mail(subject, message, 'autoluxpk@gmail.com', ['autoluxpk@gmail.com'],
                          fail_silently=False)

                send_mail(subject, message, 'autoluxpk@gmail.com', [email],
                          fail_silently=False)

                orderData = {
                    'orderNumber': order_number,
                    'success': True
                }
                return JsonResponse(orderData)
            except Exception as e:
                print('Exception: ')
                print(e)

                orderData = {
                    'errors': e,
                    'success': False
                }
                return JsonResponse(orderData)

        else:
            orderData = {
                'errors': orderForm.errors,
                'success': False
            }
            return JsonResponse(orderData)


class CarInformation(View):

    def post(self, request):
        if 'car_make_id' in request.POST:
            car_make_id = request.POST.get('car_make_id', None)
            car_model_array = CarModel.objects.filter(company_id=car_make_id).values()
            list_data = list(car_model_array)
            return JsonResponse(list_data, safe=False)
        elif 'car_model_id' in request.POST:
            car_model_id = request.POST.get('car_model_id', None)
            car_year_array = CarYear.objects.filter(model_id=car_model_id).distinct('car_year').values()
            list_data = list(car_year_array)
            return JsonResponse(list_data, safe=False)



# class ZohoView(TemplateView):
#     template_name = 'verifyforzoho.html'
