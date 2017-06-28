from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as views_auth

urlpatterns = [
    url(r'^$', views_auth.login),
#    url(r'^dashboard/', views.dashboard),
    url(r'^new/', views.collectionew, name="new_collection"),
    url(r'^login/$', views_auth.login, name="login"),
    url(r'^logout/$', views.logout ,name='logout'),
    url(r'^register/$',views.register, name='register'),
    url(r'^collections/$', views.collection, name='list_collections'),
    url(r'^collections/(?P<c_id>\d+)/$', views.collectionid, name='view_collection'),
    url(r'^collections/(?P<v_id>\d+)/uploads/$', views.collection_upload, name='collection_upload'),
    url(r'^collections/(?P<b_id>\d+)/view/$', views.collection_view, name='view collection'),
    url(r'^collections/(?P<x_id>\d+)/query/search=(?P<search>[^/]+)', views.search, name='search'),
]

