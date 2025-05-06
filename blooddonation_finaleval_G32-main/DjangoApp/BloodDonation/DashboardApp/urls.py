from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('donate/', views.add_donation_view, name='add_donation'), 
    path('request/', views.request_blood_view, name='request_blood'), 
    path('add-camp/', views.add_camp_view, name='add_camp'),
    path('search-camp/', views.search_camp_view, name='search_camp'),

]
