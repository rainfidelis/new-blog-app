from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from rainblog.sitemaps import PostSiteMap

sitemaps = {
    'posts': PostSiteMap
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rainblog.urls', namespace='blog')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]
