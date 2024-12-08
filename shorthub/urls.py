"""
URL configuration for shorthub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views
from understat.api.views import mine_league_season_data, mine_league_data, get_upcoming_fixtures

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/understat/', include('understat.api.urls')),
    path('', views.index_view, name='index'),
    path('home/', views.home_view, name='home'),
    path('historical-data/', views.league_season_form, name='historical_data'),
    path('latest-data/', views.league_form_view, name='latest_data'),
    path('upcoming-fixtures/', views.upcoming_fixtures, name='upcoming_fixtures'),
]
