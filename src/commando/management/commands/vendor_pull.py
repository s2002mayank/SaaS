import helpers
from django.conf import settings
from django.core.management import BaseCommand

STATICFILES_VENDOR_DIR=getattr(settings, "STATICFILES_VENDOR_DIR")

VENDOR_STATICFILES={
    "flowbite.min.css" : 'https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.css' ,
    "flowbite.min.js" : 'https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.js'    
}


class Command(BaseCommand):

    def handle(self, *args: any, **options: any):
        self.stdout.write("Downloading vendor files")
        completed_urls=[]
        for name, url in VENDOR_STATICFILES.items():
            out_path= STATICFILES_VENDOR_DIR/ name
            download_success= helpers.download_to_local(url, out_path)            
            if(download_success):
                completed_urls.append(url) 
            else:
                self.stdout.write(
                    self.style.ERROR(f'failed to download {url} to {out_path}')
                )                
        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write(
                self.style.SUCCESS('all vendor files have been downloaded successfully')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Couldn\'t download all vendor files')
            )