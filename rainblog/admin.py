from django.contrib import admin
from .models import Comment, Post



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ('title', 'author', 'time_created', 'time_published', 'status', 'time_updated')
    list_filter = ('title', 'author', 'status', 'time_published')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'time_published'
    raw_id_fields = ('author', )
    # ordering = ('status', 'time_published')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated', 'post')
    search_fields = ('name', 'email', 'body')