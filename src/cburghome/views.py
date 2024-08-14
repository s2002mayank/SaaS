from django.shortcuts import render
from django.http import HttpResponse
from visits.models import PageVisit

import pathlib

this_dir=pathlib.Path(__file__).resolve().parent

#  views: functions that render HTML and handle the logic behind it

def home_view(request, *args, **kwargs):    
     return about_view(request, *args, **kwargs)     

def about_view(request, *args, **kwargs):
        queryset=PageVisit.objects.all()     
        queryset_currPage=PageVisit.objects.filter(path=request.path)           
        try:
            percent=queryset_currPage.count() *100.0 / queryset.count()
        except:
            percent=0
        my_context={
        "page_title": "FutureSex/LoveSounds",
        "page_content": "Lovestoned/I think that she knows",
        "Total_page_visits":queryset.count(),
        "current_page_visits" :queryset_currPage.count(),
        "percent" : percent,        
        }  
    
        PageVisit.objects.create(path=request.path)     #fields: path, timestamp
        html_template= "home.html"        
        return render(request, html_template, my_context)

def my_old_home_page_view(request, *args, **kwargs):    
    my_title="FutureSex/LoveSounds"
    my_content="I think that she knows"
    my_context={
        "page_title": my_title,
        "page_content": my_content
        }        
    html1_=f"<h1>{my_title}</h1>" # string substitution
    html2_="<h1>{page_title}</h1><p>{page_content}</p>".format(**my_context) # unpack the dictionary    
    #format(page_content="I think that she knows", page_title="FutureSex/LoveSounds")
    return HttpResponse(html2_)


def my_ancient_home_page_view(request, *args, **kwargs):
    print(this_dir)
    html_=""        
    html_file_path= this_dir/"home.html"    
    html_=html_file_path.read_text()        
    return HttpResponse(html_)
    # return HttpResponse("<h1>FutureSex/LoveSounds</h1>")