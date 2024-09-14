from helpers.billing import (get_customer_active_subscriptions, get_subscription, cancel_subscription)

from subscriptions.models import Subscription, UserSubscription
from customers.models import Customer
from django.db.models import Q

# User is foreign key to UserSubscription
def refresh_active_users_subscriptions(
        user_ids=[], 
        active_only=True, 
        days_ago=0, 
        days_left=0, 
        day_start=0,
        day_end=0,
        verbose=False):    
    ''' --comments
    qs=UserSubscription.objects.filter(user_id=user_id)
    qs=UserSubscription.objects.all()        
    active_qs=qs.filter(status=UserSubscription.SubscriptionStatus.ACTIVE)
    trialing_qs=qs.filter(status=UserSubscription.SubscriptionStatus.TRIALING)
    qs= active_qs | trialing_qs OR
    '''
    qs=UserSubscription.objects.all()        
    if active_only:
        active_qs_lookup = (
            Q(status=UserSubscription.SubscriptionStatus.ACTIVE) |
            Q(status=UserSubscription.SubscriptionStatus.TRIALING)
        )
        '''
        qs = UserSubscription.objects.filter(active_qs_lookup)    
        qs =UserSubscription.objects.by_user_ids(user_ids=user_ids)
        '''
        qs = UserSubscription.objects.filter(active_qs_lookup)    
    if qs is not None:
        qs = qs.by_user_ids(user_ids=user_ids)
    if days_ago >-1:
        qs=qs.by_days_ago(days_ago=days_ago)
    if days_left >-1:
        qs=qs.by_days_left(days_left=days_left)
    if day_start >-1 and day_end>-1:
        qs=qs.by_range(days_start=day_start, days_end=day_end)
    complete_count=0
    qs_count=qs.count()
    for obj in qs:
        if verbose:
            print("updating user", obj.user, obj.subscription, obj.cancel_at_period_end, obj.current_period_end)
        if obj.stripe_id: 
            sub_data=get_subscription(obj.stripe_id, raw=False)
            for k, v in sub_data.items():
                setattr(obj, k, v)
            obj.save()    
            complete_count=complete_count+1
    return complete_count==qs_count

def clear_dangling_subscriptions():                    
    try:
        qs=Customer.objects.filter(stripe_id__isnull=False)
        for customer_obj in qs:
            user=customer_obj.user
            customer_stripe_id=customer_obj.stripe_id
            # print("sync {user}-{customer_stripe_id} subd and remove old subs")   
            subs=get_customer_active_subscriptions(customer_stripe_id)       
            for sub in subs:                    
                existing_user_subs_qs=UserSubscription.objects.filter(stripe_id__iexact=f"{sub.id}".strip())      
                if existing_user_subs_qs.exists():                        
                    cancel_subscription(sub.id, reason="dangling user subscription", cancel_at_period_end=False)                                              
    except:
        pass

def sync_subs_groups_permissions():
    try:
        qs=Subscription.objects.filter(active=True)
        for obj in qs:            
            # print(obj.groups.all())
            sub_perms=obj.permissions.all()
            for group in obj.groups.all():                    
                # for perm in obj.permissions.all():
                    group.permissions.set(sub_perms)
                    # group.permissions.add(perm)
            # print(obj.permissions.all())                    
    except:
        pass
    
