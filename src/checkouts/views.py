from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription
from helpers.billing import (start_checkout_session, get_checkout_session, get_subscription, get_checkout_customer_plan, cancel_subscription)
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import get_user_model


BASE_URL=settings.BASE_URL
User=get_user_model()
# Create your views here.

def product_price_redirect_view(request, price_id=None, *args, **kwargs):        
    # subscription_obj_price_id 
    # 'cause subscription obj -> product
    request.session['checkout_subscription_price_id']= price_id
    return redirect('stripe-checkout-start')

@login_required
def checkout_redirect_view(request, *args, **kwargs):
    checkout_subscription_price_id=request.session.get('checkout_subscription_price_id')
    try:
        obj=SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj=None
        if checkout_subscription_price_id is None or obj is None:
            return redirect('/pricing')
                
    customer_stripe_id= request.user.customer.stripe_id
    success_url_base=BASE_URL
    success_url_path=reverse("stripe-checkout-end")
    success_url=f"{success_url_base}{success_url_path}"    
    cancel_url_path=reverse('pricing')
    cancel_url=f"{success_url_base}{cancel_url_path}"    
    price_stripe_id=obj.stripe_id
    url =start_checkout_session(
        customer_id=customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=price_stripe_id,
        raw=False
    )
    return redirect(url)

def checkout_finalize_view(request, *args, **kwargs):
    session_id=request.GET.get('session_id')    
    # session_res -> checkout_res
    checkout_data= get_checkout_customer_plan(session_id)    
    context={"checkout": checkout_data}
    customer_id=checkout_data.pop('customer_id', None)    
    plan_id=checkout_data.pop('plan_id', None)    
    sub_stripe_id=checkout_data.pop('sub_stripe_id', None)    
    # current_period_start=checkout_data.get('current_period_start')    
    # current_period_end=checkout_data.get('current_period_end')
    subscription_data={**checkout_data}
    
    try:
        sub_obj=Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
    except:
        sub_obj=None
    try:
        user_obj=User.objects.get(customer__stripe_id=customer_id)
    except:
        user_obj=None

    _user_sub_exists=False
    _sub_options={
        "subscription": sub_obj,
        "stripe_id": sub_stripe_id, 
        "user_cancelled": False,
        **subscription_data,
    }
    try:
        _user_sub_obj=UserSubscription.objects.get(user=user_obj)
        _user_sub_exists=True
    except UserSubscription.DoesNotExist:
        _user_sub_obj=UserSubscription.objects.create(
            user=user_obj, 
            **_sub_options
            )
    except:
        _user_sub_obj=None
    if None in [user_obj, sub_obj, _user_sub_obj]:
        return HttpResponse("Error with you account. Contact admin")
    
    if _user_sub_exists:
        # cancel old subscription
        old_stripe_id=_user_sub_obj.stripe_id
        same_stripe_id= sub_stripe_id ==old_stripe_id
        if old_stripe_id is not None and not same_stripe_id:
            try:
                cancel_subscription(old_stripe_id, reason="Auto ended, new membership", feedback="other")       
            except:
                pass
        #  assign new subscription
        for k, v in _sub_options.items():
            setattr(_user_sub_obj, k, v)                
        _user_sub_obj.save()
    
    return render(request, "checkout/success.html", context)