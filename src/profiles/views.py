from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render

User=get_user_model()

# Create your views here.
@login_required
def profile_view(request, username=None, *args, **kwargs):
    User_exists= User.objects.filter(username=username).first()
    # current_user= User.objects.filter(username=request.user.id).first()
    if User_exists and User_exists.id == request.user.id:        
        return HttpResponse(f"Hi there! {username}")        
    else:                    
        return HttpResponse(f"Hi there! not current user but anyways {username}")
