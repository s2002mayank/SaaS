from django.db import models
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
import helpers.billing
from django.urls import reverse
from django.utils import timezone
import datetime

User=settings.AUTH_USER_MODEL
EMAIL_HOST_USER=settings.EMAIL_HOST_USER
ALLOW_CUSTOM_GROUPS=True
SUBSCRIPTION_PERMISSIONS=[
            ("advanced", "Advanced Perm"), #subscriptions.advanced
            ("pro", "Pro Perm"), #subscriptions.pro
            ("basic", "basic Perm"), #subscriptions.basic
            ("basic AI", "Basic AI Perm"),
        ]

# Create your models here.

# Subscription model -> name, active, groups(MtM), permissions(MtM), stripe_id
# ex-> basic plan, inactive, groups-> None, permissions ->None
class Subscription(models.Model):
    """
        Subscription -> Stripe product
    """
    name= models.CharField(max_length=120)
    active= models.BooleanField(default=True)
    groups=models.ManyToManyField(Group)
    permissions= models.ManyToManyField(Permission, 
        limit_choices_to={
        "content_type__app_label":"subscriptions", 
        "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
        }
    )
    stripe_id=models.CharField(max_length=120, null=True, blank=True)
    order=models.IntegerField(default=-1, help_text="ordering on django pricing page")
    featured=models.BooleanField(default=True, help_text="featured on django pricing page")
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    features=models.TextField(help_text="features for pricing, seperated by new line", null=True, blank=True)


    def get_features_as_list(self):
        if not self.features:
            return []        
        return [x.strip() for x in self.features.split('\n')]                    

    def save(self, *args, **kwargs):        
        if not self.stripe_id:                                  
                name=self.name
                if name!="" or name is not None:
                    self.stripe_id= helpers.billing.create_product(
                        name=name,
                        metadata={                            
                            "subscription_plan_id": self.id
                            },
                        raw=False
                        )                        
        super().save(*args, **kwargs)
        #  post- save nothing will be updated        
    
    def __str__(self):
        return f"{self.name}"
        
    class Meta:
        ordering=["order", "featured", "-updated"]
        permissions=SUBSCRIPTION_PERMISSIONS


# usersubscription model-> user(obj)(OtO), subscription(OtO), active
# ex-> user<django>, subscription<Pro plan>, inactive


class UserSubscriptionQuerySet(models.QuerySet):

        def by_range(self, days_start=7, days_end=120):
            now = timezone.now()
            days_start_from_now = now + datetime.timedelta(days=days_start)
            days_end_from_now = now + datetime.timedelta(days=days_end)
            range_start = days_start_from_now.replace(hour=0, minute=0, second=0, microsecond=0)
            range_end = days_end_from_now.replace(hour=23, minute=59, second=59, microsecond=59)

            return self.filter(
                current_period_end__gte=range_start,
                current_period_end__lte= range_end
            )        

        def by_days_left(self, days_left=7):
            now = timezone.now()
            in_n_days = now + datetime.timedelta(days=days_left)
            day_start = in_n_days.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = in_n_days.replace(hour=23, minute=59, second=59, microsecond=59)

            return self.filter(
                current_period_end__gte=day_start,
                current_period_end__lte=day_end
            )        
        
        def by_days_ago(self, days_ago=3):
            now = timezone.now()
            in_n_days = now - datetime.timedelta(days=days_ago)
            day_start = in_n_days.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = in_n_days.replace(hour=23, minute=59, second=59, microsecond=59)

            return self.filter(
                current_period_end__gte=day_start,
                current_period_end__lte=day_end
            )        
          
        def by_user_ids(self, user_ids=None):
            # qs=self.get_queryset()
            qs=self
            if isinstance(user_ids, list):
                qs = qs.filter(user_id__in=user_ids)
            elif isinstance(user_ids, int):
                qs = qs.filter(user_id__in=[user_ids])
            elif isinstance(user_ids, str):
                qs = qs.filter(user_id__in=[user_ids])
            return qs

class UserSubscriptionManager(models.Manager):
    def get_queryset(self):
        return UserSubscriptionQuerySet(self.model, using=self._db)
    
    # def by_user_ids(self, user_ids=None):
    #     return self.get_queryset().by_user_ids(user_ids=user_ids)
        
class UserSubscription(models.Model):

    class SubscriptionStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        TRIALING = 'trialing', 'Trialing'
        INCOMPLETE = 'incomplete', 'Incomplete'
        INCOMPLETE_EXPIRED = 'incomplete_expired', 'Incomplete Expired'
        PAST_DUE = 'past_due', 'Past Due'
        CANCELED = 'canceled', 'Canceled'
        UNPAID = 'unpaid', 'Unpaid'
        PAUSED = 'paused', 'Paused'

    user=models.OneToOneField(User, on_delete=models.CASCADE)
    subscription=models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active=models.BooleanField(default=True)
    stripe_id=models.CharField(max_length=120, null=True, blank=True)
    user_cancelled= models.BooleanField(default=False)
    original_period_start=models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    current_period_start=models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    current_period_end=models.DateTimeField(auto_now=False, auto_now_add=False,  blank=True, null=True)
    cancel_at_period_end=models.BooleanField(default=False)
    status=models.CharField(max_length=20, choices=SubscriptionStatus.choices, null=True, blank=True)

    objects=UserSubscriptionManager()
    # def __Str__(self):
    #     return f"{self.user}_{self.subscription}"

    def is_active_status(self):
        return self.status in [self.SubscriptionStatus.ACTIVE, self.SubscriptionStatus.TRIALING]
    
    def get_absolute_url(self):
        return reverse("user_subscription")
    
    def get_cancel_url(self):
        return reverse("user_subscription_cancel")

    def plan_name(self):
        if not self.subscription:
            return None
        return self.subscription.name
    
    def serialize(self):
        return {
            "Plan" : self.plan_name,
            "Current_period_start":self.current_period_start,
            "Current_period_end":self.current_period_end,
            "Status": self.status,
        }

    @property
    def billing_cycle_anchor(self):
        if not self.current_period_end:
            return None
        return int(self.current_period_end.timestamp)
    
    def save(self, *args, **kwargs):
        if (self.original_period_start is None and self.current_period_end is not None):
            self.original_period_start =self.current_period_end
        super().save(*args, **kwargs)
        


# subscriptionprice-> subscription(ForeignKey),  interval, price, stripe_id, active(future work)
# ex-> subscription<advanced plan>, monthly, 2.99, stripe_id<intangible>
class SubscriptionPrice(models.Model):
    """
        Subscription prie -> Stripe price
    """
    class IntervalChoices(models.TextChoices):
        MONTHLY="month", "Monthly"
        YEARLY="year", "Yearly"

    subscription=models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)                
    interval=models.CharField(max_length=120, default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price=models.DecimalField(max_digits=10, decimal_places=2, default=2.99)
    stripe_id=models.CharField(max_length=120, null=True, blank=True)    
    order=models.IntegerField(default=-1, help_text="ordering on django pricing page")
    featured=models.BooleanField(default=True, help_text="featured on django pricing page")
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)    

    class Meta:
        ordering=["subscription__order", "order", "featured", "-updated"]

    
    def get_checkout_url(self):
        return reverse("sub-price-checkout", kwargs={"price_id": int(self.id)})

    
    @property        
    def display_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_as_list()
        
    @property
    def display_sub_name(self):
        if not self.subscription:
            return "to be announced soon"
        return self.subscription.name
    
    @property
    def stripe_currency(self):        
        return "usd"
    
    @property
    def stripe_price(self):
        '''
        remove decimal places        
        '''
        return int(self.price *100)
    
    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    
    def __str__(self):
        return f"{self.interval}ly" # haha
    
    def save(self, *args, **kwargs):
        if not self.stripe_id and self.product_stripe_id is not None:
            stripe_id= helpers.billing.create_price(
            currency=self.stripe_currency,
            unit_amount=self.stripe_price,
            interval=self.interval,
            product=self.product_stripe_id,
            metadata={
                "subscription_plan_price_id" :self.id
            },
            raw=False
            )
            self.stripe_id=stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs=SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval=self.interval
            ).exclude(id=self.id)            
            qs.update(featured=False)

def user_sub_post_save(sender, instance, *args, **kwargs):    
    subject = f"Subscription Confirmed: Tier-{instance.subscription.name}"
    message = "Thank you for subscribing to our service!"
    from_email = EMAIL_HOST_USER
    recipient_list = [instance.user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=True,)
    
    user_sub_instance= instance
    user=user_sub_instance.user
    subscription_obj= user_sub_instance.subscription
    groups_ids=[]
    if subscription_obj is not None:
        groups= subscription_obj.groups.all()
        groups_ids=groups.values_list("id", flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs=Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs=subs_qs.exclude(id=subscription_obj.id)
        subs_groups=subs_qs.values_list("groups__id", flat=True)
        subs_groups_set=set(subs_groups)        
        # groups_ids=groups.values_list("id", flat=True)
        current_groups=user.groups.all().values_list("id", flat=True)        
        groups_ids_set=set(groups_ids)
        current_groups_set=set(current_groups) - subs_groups_set
        final_groups_ids= list(groups_ids_set | current_groups_set)
        user.groups.set(final_groups_ids)        


post_save.connect(user_sub_post_save, sender=UserSubscription)    




