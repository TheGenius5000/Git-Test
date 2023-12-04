from django.shortcuts import render
from django.http import Http404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.views.generic.edit import DeleteView
from .models import Notes
from .forms import WriterForm


# Create your views here.

class WriterDeleteView(DeleteView):
    model = Notes
    success_url = '/smart/writer'

class WriterUpdateView(UpdateView):
    model = Notes
    success_url = '/smart/writer'
    form_class = WriterForm


class WriterCreateView(CreateView):
    model = Notes
    success_url = '/smart/writer'
    form_class = WriterForm


class WriterListView(ListView):
    model = Notes
    context_object_name = "notes"
    template_name = "writer/notes_list.html"


class WriterDetailView(DetailView):
    model = Notes
    context_object_name = "note"
