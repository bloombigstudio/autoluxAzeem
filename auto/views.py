from django.shortcuts import render
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)


class Interior(TemplateView):
    template_name = 'interior.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)


class Single(TemplateView):
    template_name = 'single.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)


class Contact(TemplateView):
    template_name = 'contact.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)



class About(TemplateView):
    template_name = 'about.html'

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)


