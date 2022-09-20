from django.urls import path
from . import views


urlpatterns = [
    path('getprofile', views.getUserProfile),
    path('getprofile/<int:profileId>/', views.getProfileById),
]