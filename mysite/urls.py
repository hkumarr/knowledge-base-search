"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
#from django.conf.urls import include, url
#from django.contrib import admin
#
from django.conf.urls import patterns, include, url
from views import hello,search_form,search,triple
import settings

urlpatterns = patterns('',
    url(r'^hello/$', hello),
    url(r'^search_form/$', search_form),
    url(r'^search/$', search),
    url(r'^triple/$',triple),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
{ 'document_root': settings.SITE_MEDIA_ROOT }),
)
'''urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]'''
