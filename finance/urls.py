from django.urls import path
from finance import views
from . import views

urlpatterns = [
    path('register/',views.register_user, name='home'),
]
