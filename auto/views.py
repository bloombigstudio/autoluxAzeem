from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from auto.forms import *
from auto.models import *
from autolux import settings
import json
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.http import JsonResponse

class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        signUpForm = SignUpForm()
        signInForm = SignInForm()
        all_products = Product.objects.all()
        all_cars = CarCompany.objects.all()

        args = {'signUp': signUpForm, 'signIn': signInForm, 'all_products': all_products, "stripe_key": settings.STRIPE_PUBLIC_KEY, 'all_cars': all_cars }
        return render(request, self.template_name,args)

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
    signUpForm = SignUpForm()
    signInForm = SignInForm()

    def get(self, request, *args, **kwargs):
        item_name = kwargs.get('item_name')
        Interior = Product.objects.filter(product_category=item_name)
        page_title = item_name

        if Interior.count() > 3:
            interior_first_row = Interior[:3]
            interior_else_rows = Interior[3:]
        else:
            interior_first_row = Interior
            interior_else_rows = None

        args = {'signUp': self.signUpForm, 'signIn': self.signInForm,'interior_first_row': interior_first_row, 'interior_else_rows': interior_else_rows, 'page_title': page_title}

        return render(request, self.template_name,args)

    def post(self, request, **kwargs):
        page_title = kwargs.get('item_name')

        car_make = request.POST['selected_car_make']
        car_model = request.POST['selected_car_model']
        car_year = request.POST['selected_car_year']

        query = Product.objects.filter(cars_related_name__car_make=car_make.strip(),cars_related_name__company_related_name__car_model=car_model.strip(),cars_related_name__company_related_name__model_related_name__car_year=car_year.strip())
        if query.count() > 3:
            interior_first_row = query[:3]
            interior_else_rows = query[3:]
        else:
            interior_first_row = query
            interior_else_rows = None

        args = {'signUp': self.signUpForm, 'signIn': self.signInForm, 'interior_first_row': interior_first_row,'interior_else_rows': interior_else_rows, 'page_title': page_title}

        return render(request, self.template_name,args)


class ProductDescription(TemplateView):
    template_name = 'product_description.html'

    def get(self, request, *args, **kwargs):

        signUpForm = SignUpForm()
        signInForm = SignInForm()
        item_id = kwargs.get('id')
        selected_item = ProductSpecification.objects.filter(product_id_id=item_id)
        new_arrivals = Product.objects.all().order_by('-id')[:4]
        args = {'signUp': signUpForm, 'signIn': signInForm,'selected_item': selected_item, 'new_arrivals': new_arrivals}
        return render(request, self.template_name,args)


class Contact(TemplateView):
    template_name = 'contact.html'

    def get(self, request, *args, **kwargs):
        signUpForm = SignUpForm()
        signInForm = SignInForm()

        args = {'signUp': signUpForm, 'signIn': signInForm }
        return render(request, self.template_name,args)



class About(TemplateView):
    template_name = 'about.html'

    def get(self, request, *args, **kwargs):
        signUpForm = SignUpForm()
        signInForm = SignInForm()

        args = {'signUp': signUpForm, 'signIn': signInForm }
        return render(request, self.template_name,args)



# Chaipiiiiiiii :P
class Login(TemplateView):
    template_name = 'index.html'

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

        args = {'orderForm': orderForm, 'payment_method': payment_method,'token':token }

        return render(request,self.template_name,args)

    def post(self, request, **kwargs):
        orderForm = UserOrderForm(request.POST)

        if orderForm.is_valid():
            first_name = orderForm.cleaned_data['first_name']
            last_name = orderForm.cleaned_data['last_name']
            email = orderForm.cleaned_data['email']
            address = orderForm.cleaned_data['address']
            contact_number = orderForm.cleaned_data['contact_number']
            payment_method = request.POST['payment_method']
            token = request.POST['token']
            user = orderForm.save()

            json_order = request.POST['cart_info']
            cart_object = json.loads(json_order)

            total_bill = 0
            for order in cart_object["products"]:
                total_bill = total_bill + float(order['price'])
                if payment_method == "Online Payment":
                    user_order = Order(user=user, item_id=order['id'], item_name=order['name'],item_price=order['price'], payment_status=True)
                    user_order.save()

                else:
                    direct_order = Order(user=user, item_id=order['id'], item_name=order['name'],item_price=order['price'], payment_status=False)
                    direct_order.save()

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


        return render(request, self.template_name)


class CarInformation(View):

    def post(self, request):
        if 'car_make_id' in request.POST:
            car_make_id = request.POST.get('car_make_id', None)
            car_model_array = CarModel.objects.filter(company_id=car_make_id).values()
            list_data = list(car_model_array)
            return JsonResponse(list_data, safe=False)
        elif 'car_model_id' in request.POST:
            car_model_id = request.POST.get('car_model_id', None)
            car_year_array = CarYear.objects.filter(model_id=car_model_id).values()
            list_data = list(car_year_array)
            return JsonResponse(list_data, safe=False)

