from typing import Any
from django.core.management.base import BaseCommand

from subscriptions import utils as sub_utils

class Command(BaseCommand):

    def handle(self, *args :Any , **kwargs: Any):                    
        try:
            sub_utils.sync_subs_groups_permissions()               
            self.stdout.write(
                self.style.SUCCESS("Sync complete")
            )
        except:
            self.stdout.write(
                self.style.ERROR("Sync incomplete")
            )
        
