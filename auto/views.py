import uuid

from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from urllib.parse import urlparse

from auto.filters import ProductFilter
from auto.forms import *
from auto.models import *
from autolux import settings
import json
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.http import JsonResponse, BadHeaderError, HttpResponse

signUpForm = SignUpForm()
signInForm = SignInForm()
all_cars = CarCompany.objects.all()
product_list = Product.objects.all()
params = {'signUp': signUpForm, 'signIn': signInForm, "all_cars": all_cars}


class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        product_filter = ProductFilter(request.GET, queryset=product_list)
        silder_images = SliderImage.objects.all()

        all_products = Product.objects.all().order_by('-id')
        home_categories_images = HomePageCategoriesImages.objects.latest()

        params['all_products'] = all_products
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


class Products(TemplateView):
    template_name = 'products.html'
    paginator = None

    def get(self, request, *args, **kwargs):
        item_name = kwargs.get('item_name')

        category_wise_images = CategoryWiseImageBackground.objects.latest()
        search_results = request.GET['product_title'] if "product_title" in request.GET else ""
        product_filter = ProductFilter(request.GET, queryset=product_list)
        if item_name == "SearchResults":

            page_data = product_filter.qs
            params['page_data'] = page_data
            params['page_title'] = "Search Results"
            params['item_category'] = item_name
            params['searched_item'] = search_results
            params['category_wise_images'] = category_wise_images

            return render(request, self.template_name, params)

        elif item_name == "Search" and Products.paginator:
            page = request.GET.get('page', 1)
            try:
                page_data = Products.paginator.page(page)
            except PageNotAnInteger:
                page_data = Products.paginator.page(1)
            except EmptyPage:
                page_data = Products.paginator.page(Products.paginator.num_pages)

            params['page_data'] = page_data
            params['category_wise_images'] = category_wise_images

            return render(request, self.template_name, params)
        else:
            Interior = Product.objects.filter(product_category__iexact=item_name)
            page_title = item_name

            page = request.GET.get('page', 1)
            Products.paginator = Paginator(Interior, 12)
            try:
                page_data = Products.paginator.page(page)
            except PageNotAnInteger:
                page_data = Products.paginator.page(1)
            except EmptyPage:
                page_data = Products.paginator.page(Products.paginator.num_pages)


            params['page_data'] = page_data
            if page_title == "Suvs":
                params['page_title'] = "4x4/SUV items"
            elif page_title == 'Utilites':
                params['page_title'] = "Outdoor Utilities"
            else:
                params['page_title'] = page_title

            params['filter'] = product_filter
            params['item_category'] = item_name
            params['searched_item'] = search_results
            params['category_wise_images'] = category_wise_images

            return render(request, self.template_name,params)

    def post(self, request, **kwargs):
        page_title = kwargs.get('item_name')
        product_filter = ProductFilter(request.GET, queryset=product_list)

        if page_title == "Search":
            if 'sorting-price' not in request.POST:
                car_make = request.POST['selected_car_make']
                car_model = request.POST['selected_car_model']
                car_year = request.POST['selected_car_year']

                query = Product.objects.filter(cars_related_name__car_year=car_year.strip(),cars_related_name__model__car_model= car_model.strip(),cars_related_name__model__company__car_make=car_make.strip())
                # query = Product.objects.filter(cars_related_name__car_make=car_make.strip(),cars_related_name__company_related_name__car_model=car_model.strip(),cars_related_name__company_related_name__model_related_name__car_year=car_year.strip())

                params['selected_car_make'] = request.POST['selected_car_make']
                params['selected_car_model'] = request.POST['selected_car_model']
                params['selected_car_year'] = request.POST['selected_car_year']

            # elif 'sorting-price' in request.POST and request.POST['sorting-price'] != "":
            else:
                make = request.POST['searched-car-make']
                model = request.POST['searched-car-model']
                year = request.POST['searched-car-year']
                price = request.POST['sorting-price']
                order = request.POST['sorting-order']
                items = request.POST['sorting-items']
                category = request.POST['categories_search']
                new_price = [x.strip() for x in price.split('-')]
                min_price = new_price[0].split('s')[1]
                max_price = new_price[1].split('s')[1]
                query = ""
                sorting_order = "product_price"
                if order == "High to low":
                    sorting_order = "-product_price"

                if category == 'All':
                    query = Product.objects.filter(product_price__range=(min_price, max_price),
                                                   cars_related_name__model__company__car_make=make.strip(),
                                                   cars_related_name__model__car_model=model.strip(),
                                                   cars_related_name__car_year=year.strip()).order_by(sorting_order)
                else:
                    query = Product.objects.filter(product_price__range=(min_price, max_price),
                                                   cars_related_name__model__company__car_make=make.strip(),
                                                   cars_related_name__model__car_model=model.strip(),
                                                   cars_related_name__car_year=year.strip()).filter(product_category=category).order_by(sorting_order)

                if items != "All":
                    query = query[:int(items)]

                params['page_title'] = "Search By Car"
                params['selected_car_make'] = request.POST['searched-car-make']
                params['selected_car_model'] = request.POST['searched-car-model']
                params['selected_car_year'] = request.POST['searched-car-year']

        else:
            price = request.POST['sorting-price']
            order = request.POST['sorting-order']
            items = request.POST['sorting-items']
            searched_item = request.POST['searched-item']
            new_price = [x.strip() for x in price.split('-')]
            min_price = new_price[0].split('s')[1]
            max_price = new_price[1].split('s')[1]
            query = ""
            sorting_order = "product_price"
            if order == "High to low":
                sorting_order = "-product_price"
            elif order == "Z to A":
                sorting_order = "-product_title"
            elif order == "A to Z":
                sorting_order = "product_title"

            if page_title == "SearchResults":
                query = Product.objects.filter(product_title__icontains=searched_item ,product_price__range=(min_price, max_price)).order_by(sorting_order)
                if items != "All":
                    query = query[:int(items)]
            else:
                query = Product.objects.filter(product_category=page_title, product_price__range=(min_price, max_price)).order_by(sorting_order)
                if items != "All":
                    query = query[:int(items)]
            params['searched_item'] = searched_item
            params['page_title'] = "Filtered Data"

        page = request.GET.get('page', 1)
        Products.paginator = Paginator(query, 12)
        try:
            page_data = Products.paginator.page(page)
        except PageNotAnInteger:
            page_data = Products.paginator.page(1)
        except EmptyPage:
            page_data = Products.paginator.page(Products.paginator.num_pages)

        params['page_data'] = page_data
        params['filter'] = product_filter
        params['item_category'] = page_title

        return render(request, self.template_name,params)


class ProductDescription(TemplateView):
    template_name = 'product_description.html'

    def get(self, request, *args, **kwargs):
        product_filter = ProductFilter(request.GET, queryset=product_list)
        params['filter'] = product_filter

        item_id = kwargs.get('id')
        selected_item = ProductSpecification.objects.filter(product_id_id=item_id)
        new_arrivals = Product.objects.all().order_by('-id')[:4]

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



# Chaipiiiiiiii :P
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
            'orderBackgroundImage': orderBackgroundImage.background_image.url
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

                if(request.POST.get('cart_info') == None):
                    orderData = {
                        'errors': 'You do not have any items in your cart',
                        'success': False
                    }
                    return JsonResponse(orderData)

                user = orderForm.save()

                order_number = uuid.uuid4().hex[:6].upper()
                json_order = request.POST['cart_info']
                cart_object = json.loads(json_order)

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

                for order in cart_object["products"]:
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

                orderData = {
                    'orderNumber': order_number,
                    'success': True
                }
                return JsonResponse(orderData)
            except Exception as e:
                print('Exception: ')
                print(e)

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
