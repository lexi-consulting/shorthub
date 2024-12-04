from django.shortcuts import render

def index_view(request):
    return render(request, 'base/index.html')

def home_view(request):
    return render(request, 'base/home.html')  