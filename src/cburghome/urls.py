"""
URL configuration for cburghome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from checkouts import views as checkout_views
from subscriptions.views import (subscription_pricing_view, user_subscription_view, user_subscription_cancel_view)
from .views import (home_view, helper_view)


# urls: route traffic to views
# path('url_name', view)            
urlpatterns = [       
    # helper
    path("helper/", helper_view,name="helper"),
    # homepage
    path('', home_view,name="home"), # Home page    
    path('dashboard/', include('dashboard.urls')),

    # authentication
    path('accounts/', include('allauth.urls')), # django all-auth uses this

    # user profiles
    path('profiles/', include('profiles.urls')),            

    # pricing
    path('pricing/<str:interval>/', subscription_pricing_view, name="pricing_interval"),
    path('pricing/', subscription_pricing_view, name="pricing"),

    # checkout session
    path("checkout/sub-price/<int:price_id>/", checkout_views.product_price_redirect_view, name="sub-price-checkout"),    
    path("checkout/start/", checkout_views.checkout_redirect_view, name="stripe-checkout-start"),
    path("checkout/success/", checkout_views.checkout_finalize_view, name="stripe-checkout-end"), 

    # Subscription details
    path("accounts/billing/", user_subscription_view, name='user_subscription'),
    path("accounts/billing/cancel", user_subscription_cancel_view, name='user_subscription_cancel'),

    # admin    
    path('admin/', admin.site.urls),    
]
