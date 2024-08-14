from django.db import models

# Create your models here.
# python manage.py makemigrations
# python manage.py migrate

# table
class PageVisit(models.Model): # pageVisits -> page_visits
    # id -> primary key, hidden, created automatically : 1,2,3,4,5, ... 
    path=models.TextField(blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    timestamp=models.DateTimeField(auto_now_add=True)    