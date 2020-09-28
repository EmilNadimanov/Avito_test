from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('query_archive', views.query_archive, name='query_archive'),
    path('<str:short_link>', views.redirect, name='redirect'),
]
