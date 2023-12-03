from django.shortcuts import render
from django.http import Http404
from django.views.generic import CreateView, ListView, DetailView

from .models import Notes


# Create your views here.

class WriterCreateView(CreateView):
    model = Notes
    fields = ['title', 'text']
    success_url = '/smart/writer'
    template_name = "writer/write-form.html"


class WriterListView(ListView):
    model = Notes
    context_object_name = "notes"
    template_name = "writer/notes_list.html"


class WriterDetailView(DetailView):
    model = Notes
    context_object_name = "note"
