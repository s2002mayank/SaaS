from django.urls import path, include
from .views import *
urlpatterns = [
    path('home/', landing_page_view, name="home_page"),
]