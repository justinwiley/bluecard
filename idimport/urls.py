from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index,
        name='index'),
    url(r'^login/$', views.login_user,
        name='login'),
    url(r'^logout/$', views.logout_user,
        name='logout'),
    url(r'^customers/new$', views.new,
        name='new'),
    url(r'^customers/(?P<customer_id>[0-9]+)/$', views.customer,
        name='customer'),
    url(r'^customers/(?P<customer_id>[0-9]+)/upload$', views.upload,
        name='upload'),
    url(r'^customers/(?P<customer_id>[0-9]+)/imports$', views.imports,
        name='imports'),
    url(r'^customers/(?P<customer_id>[0-9]+)/status$', views.status,
        name='status'),
]
