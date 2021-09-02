from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset()\
                                            .filter(status='published')

class Post(models.Model):

    objects = models.Manager()
    published = PublishedManager()

    STATUS_CHOICES = (('draft', 'Draft'),
                      ('published', 'Published'),
                )

    title = models.CharField(max_length=250)
    slug = models.CharField(max_length=250, 
                            unique_for_date='time_published')
    tags = TaggableManager()
    author = models.ForeignKey(User, 
                                on_delete=models.CASCADE,
                                related_name='blog_posts')
    body = models.TextField('Post')
    time_published = models.DateTimeField(default=timezone.now)
    time_created = models.DateTimeField('Created', auto_now_add=True)
    status = models.CharField(max_length=10, 
                            choices=STATUS_CHOICES, 
                            default='draft')

    class Meta:
        ordering = ('-time_published',)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail',
                        args=[self.time_published.year,
                              self.time_published.month,
                              self.time_published.day,
                              self.slug])



class Comment(models.Model):
    post = models.ForeignKey(Post, 
                            on_delete=models.CASCADE, 
                            related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self) -> str:
        return f'Comment by {self.name} on {self.post}'