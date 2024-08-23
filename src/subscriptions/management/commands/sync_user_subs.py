from typing import Any
from django.core.management.base import BaseCommand

from subscriptions import utils as sub_utils

class Command(BaseCommand):    
    def add_arguments(self, parser):
            parser.add_argument("--day-start", default=0, type=int)          
            parser.add_argument("--day-end", default=0, type=int)          
            parser.add_argument("--days-left", default=0, type=int)          
            parser.add_argument("--days-ago", default=0, type=int)          
            parser.add_argument("--clear-dangling", action="store_true", default=False)          
    def handle(self, *args :Any , **options: Any):                                          
        try:                        
            # python manage.py sync_user_subs --clear_dangling
            # print(options) 
            # options has "clear_dangling" set to False 
            day_start=options.get("day-start") 
            day_end=options.get("day_end") 
            days_ago=options.get("days_ago") 
            days_left=options.get("days_left")
            clear_dangling=options.get("clear_dangling")
            if clear_dangling:
                # clear dangling not in use active subs in stripe
                sub_utils.clear_dangling_subscriptions()
            else:
                # sync active subs
                sub_utils.refresh_active_users_subscriptions(days_ago=days_ago, days_left=days_left,active_only=True)
            self.stdout.write(
                self.style.SUCCESS("Removed all Dangling subs")
            )                
        except:
            self.stdout.write(
                self.style.WARNING("Dangling subs still exist...")
            )