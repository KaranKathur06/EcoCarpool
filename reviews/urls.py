from django.urls import path
from . import views

app_name = 'reviews'
urlpatterns = [
    path('', views.ReviewListView.as_view(), name='review-list'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
]