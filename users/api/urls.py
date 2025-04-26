from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

app_name = 'users_api'

urlpatterns = [
    path('', include(router.urls)),
]