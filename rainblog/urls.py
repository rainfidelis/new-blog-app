from django.urls import path
from .views import (PostListView, 
                    post_detail_view, 
                    post_list_view,
                    post_share_view,
                    post_search_view,
                    )
from .feeds import LatestPostFeed


app_name = 'blog'
urlpatterns = [
    # path('', PostListView.as_view(), name='home'),
    path('', post_list_view, name='home'),
    path('tag/<slug:tag_slug>', post_list_view, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', post_detail_view, name='detail'),
    path('<int:post_id>/share/', post_share_view, name='post_share'),
    path('feed/', LatestPostFeed(), name='post_feed'),
    path('search/', post_search_view, name='post_search'),
]
