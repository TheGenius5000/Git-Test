from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# Create your views here.
class HomeView(TemplateView):
    template_name = 'home/index.html'
    extra_context = {'today': datetime.today()}


class AuthorisedView(LoginRequiredMixin, TemplateView):
    template_name = 'home/authorised.html'
    login_url = '/admin'

