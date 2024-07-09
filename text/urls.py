from django.urls import path
from . import views

urlpatterns = [
    path('',views.text, name = 'home'),
    path('summarize/',views.summarize, name = 'summarize'),

]