from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from auto.forms import *
from auto.models import *
from autolux import settings
import json
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        signUpForm = SignUpForm()
        signInForm = SignInForm()
        all_products = Product.objects.all()

        args = {'signUp': signUpForm, 'signIn': signInForm, 'all_products': all_products, "stripe_key": settings.STRIPE_PUBLIC_KEY }
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

    def get(self, request, *args, **kwargs):
        item_name = kwargs.get('item_name')
        Interior = Product.objects.filter(product_category=item_name)
        signUpForm = SignUpForm()
        signInForm = SignInForm()
        page_title = item_name

        if Interior.count() > 3:
            interior_first_row = Interior[:3]
            interior_else_rows = Interior[3:]
        else:
            interior_first_row = Interior
            interior_else_rows = None

        args = {'signUp': signUpForm, 'signIn': signInForm,'interior_first_row': interior_first_row, 'interior_else_rows': interior_else_rows, 'page_title': page_title}

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


# def online_payment(request):
#     global token
#     new_car = Car(
#         product = "1",
#         car_make="Honda",
#         car_model="Civic",
#         car_year="2017-2018"
#     )
#     if request.method == "POST":
#         token = request.POST.get("stripeToken")
#     try:
#         charge = stripe.Charge.create(
#             amount=2000,
#             currency="pkr",
#             source=token,
#             description="The product charged to the user"
#         )
#
#         new_car.charge_id = charge.id
#
#     except stripe.error.CardError as ce:
#         return False, ce
#
#     else:
#         new_car.save()
#         return redirect("thank_you_page")
        # The payment was successfully processed, the user's card was charged.
        # You can now redirect the user to another page or whatever you want


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
        user_order = Order

        if orderForm.is_valid():
            first_name = orderForm.cleaned_data['first_name']
            last_name = orderForm.cleaned_data['last_name']
            email = orderForm.cleaned_data['email']
            address = orderForm.cleaned_data['address']
            contact_number = orderForm.cleaned_data['contact_number']
            payment_method = request.POST['payment_method']
            token = request.POST['token']
            user = orderForm.save()

            # if payment_method == "Online Payment":
            #     user = UserWithoutAccount(first_name = first_name, last_name = last_name, contact_number=contact_number,address=address, email=email)

            json_order = request.POST['cart_info']
            cart_object = json.loads(json_order)

            total_bill = 0
            for order in cart_object["products"]:
                total_bill = total_bill + float(order['price'])
                if payment_method == "Online Payment":
                    user_order = Order(user=user,item_id=order['id'],item_name=order['name'],item_price=order['price'], payment_status=True)
                    try:
                        charge = stripe.Charge.create(
                            amount=int(total_bill),
                            currency="usd",
                            source=token,
                            description="The product charged to the user"
                        )
                        user_order.charge_id = charge.id
                    except stripe.error.CardError as ce:
                        return False, ce
                    else:
                        user_order.save()
                else:
                    direct_order = Order(user=user, item_id=order['id'], item_name=order['name'],item_price=order['price'], payment_status=False)
                    direct_order.save()
            # if payment_method == "Online Payment":
            #     try:
            #         charge = stripe.Charge.create(
            #             amount=total_bill,
            #             currency="pkr",
            #             source=settings.STRIPE_PUBLIC_KEY,
            #             description="The product charged to the user"
            #         )
            #
            #         user_order.charge_id = charge.id
            #
            #     except stripe.error.CardError as ce:
            #         return False, ce
            #
            #     else:
            #         user_order.save()
            #         return redirect("index")
            # The payment was successfully processed, the user's card was charged.
            # You can now redirect the user to another page or whatever you want

        return render(request, self.template_name)






