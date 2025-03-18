from django.views.generic import ListView, DetailView
from .models import Review

class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'

class ReviewDetailView(DetailView):  # Add this class
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'