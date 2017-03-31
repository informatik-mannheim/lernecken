from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^buchungen/(?P<facility>[gh])/$', views.bookings, name='bookings'),
    url(r'^status/(?P<facility>[gh])/$', views.status, name='status'),
    url(r'^logout/$', views.logout, name='logout'),
]