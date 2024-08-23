from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPrice, UserSubscription
from helpers.billing import get_subscription, cancel_subscription
from django.contrib import messages
import subscriptions.utils as sub_utils

@login_required
def user_subscription_view(request, *args, **kwargs):
    user_sub_obj, created= UserSubscription.objects.get_or_create(user=request.user)
    sub_data=user_sub_obj.serialize()    
    if request.method=="POST":
        finished=sub_utils.refresh_active_users_subscriptions(user_ids=[request.user.id], active_only=False)
        if finished:                
            messages.success(request, "your plan details have been refreshed.")
        else:
            messages.error(request, "your plan details have not been refreshed. Try Again.")
        return redirect(user_sub_obj.get_absolute_url())    
    return render(request, "subscriptions/user_detail_view.html",{'subscription': sub_data, "user_sub_obj": user_sub_obj})

@login_required
def user_subscription_cancel_view(request, *args, **kwargs):
    user_sub_obj, created= UserSubscription.objects.get_or_create(user=request.user)
    sub_data=user_sub_obj.serialize()    
    if request.method=="POST":        
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:             
            sub_data=cancel_subscription(
                user_sub_obj.stripe_id,
                reason="user wanted to end",
                feedback="other",         
                cancel_at_period_end=user_sub_obj.cancel_at_period_end,                      
                raw=False)
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()            
            messages.success(request, "your plan has been cancelled.")
        return redirect(user_sub_obj.get_absolute_url())    
    return render(request, "subscriptions/user_sub_cancel_view.html",{'subscription': sub_data, "user_sub_obj": user_sub_obj})

# Create your views here.
def subscription_pricing_view(request, interval="month", *args, **kwargs):
    qs=SubscriptionPrice.objects.filter(featured=True)
    inv_mo=SubscriptionPrice.IntervalChoices.MONTHLY
    inv_yr=SubscriptionPrice.IntervalChoices.YEARLY        
    active=inv_mo
    obj_qs=qs.filter(interval=inv_mo)        
    url_path_name= "pricing_interval"
    mo_url=reverse(url_path_name, kwargs={"interval": inv_mo})
    yr_url=reverse(url_path_name, kwargs={"interval": inv_yr})    
    if(interval=="year"):   
        active=inv_yr
        obj_qs=qs.filter(interval=inv_yr)        
    return render(request, "subscriptions/pricing.html", {
        "obj_qs":obj_qs,
        "mo_url":mo_url,
        "yr_url": yr_url,
        "active": active
        }
    )

