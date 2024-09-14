from django.shortcuts import render

# Create your views here.
def landing_page_view(request, *args, **kwargs):
    return render(request, "dashboard/main.html", {})
    pass    