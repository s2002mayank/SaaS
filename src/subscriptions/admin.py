from django.contrib import admin
from .models import Subscription, UserSubscription, SubscriptionPrice

# Register your models here.


# subscription is foreign key to subscription price
class SubscriptionPrice(admin.TabularInline):
    model=SubscriptionPrice
    readonly_fields=['stripe_id']
    extra=0
    can_delete=False

class SubscriptionAdmin(admin.ModelAdmin):
    inlines=[SubscriptionPrice]
    list_display=["name", "active"]    
    readonly_fields=["stripe_id"]

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription)