from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tsp, name='tsp'),
    url(r'trip/',views.trip , name='trip'),
]
