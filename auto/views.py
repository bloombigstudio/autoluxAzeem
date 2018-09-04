from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from auto.forms import *
from auto.models import *


class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        signUpForm = SignUpForm()
        signInForm = SignInForm()
        all_products = Product.objects.all()

        args = {'signUp': signUpForm, 'signIn': signInForm, 'all_products': all_products }
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


class Interior(TemplateView):
    template_name = 'interior.html'

    def get(self, request, *args, **kwargs):
        Interior = Product.objects.filter(product_category='Interior')
        page_title = 'Interior'

        if Interior.count() > 3:
            interior_first_row = Interior[:3]
            interior_else_rows = Interior[3:]
        else:
            interior_first_row = Interior
            interior_else_rows = None

        args = {'interior_first_row': interior_first_row, 'interior_else_rows': interior_else_rows, 'page_title': page_title}

        return render(request, self.template_name,args)


class Exterior(TemplateView):
    template_name = 'interior.html'

    def get(self, request, *args, **kwargs):
        Interior = Product.objects.filter(product_category='Exterior')
        page_title = 'Exterior'

        if Interior.count() > 3:
            interior_first_row = Interior[:3]
            interior_else_rows = Interior[3:]
        else:
            interior_first_row = Interior
            interior_else_rows = None

        args = {'interior_first_row': interior_first_row, 'interior_else_rows': interior_else_rows, 'page_title': page_title}

        return render(request, self.template_name,args)



class Single(TemplateView):
    template_name = 'single.html'

    def get(self, request, *args, **kwargs):
        item_id = kwargs.get('id')
        selected_item = ProductSpecification.objects.filter(product_id_id=item_id)
        new_arrivals = Product.objects.all().order_by('-id')[:4]
        args = {'selected_item': selected_item, 'new_arrivals': new_arrivals}
        return render(request, self.template_name,args)


class Contact(TemplateView):
    template_name = 'contact.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)



class About(TemplateView):
    template_name = 'about.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)



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


