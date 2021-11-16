import time

from django.shortcuts import get_object_or_404, render
from .models import Post
from django.core.paginator import (
                Paginator, 
                EmptyPage, 
                PageNotAnInteger
                )
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from taggit.models import Tag
from .forms import EmailPostForm, CommentForm, SearchForm


# Class Based Views
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/index.html'


class PostDetailView(DetailView):
    post = Post()



# function_based_views
def post_list_view(request, tag_slug=None):

    object_list = Post.published.all()

    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        # Deliver the provided page number
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page
        posts = paginator.page(paginator.num_pages)

    return render(request, 
                  'blog/post/index.html', 
                  {'page':page,
                    'posts':posts,
                    'tag':tag})


def post_detail_view(request, year, month, day, post):
    
    post = get_object_or_404(Post, slug=post,
                                status='published',
                                time_published__year=year,
                                time_published__month=month,
                                time_published__day=day)
    # List of all active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        
        if comment_form.is_valid():
            # if form is valid, create form but don't save to db
            new_comment = comment_form.save(commit=False)
            # link comment to current post
            new_comment.post = post
            # save comment to db
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar posts
    post_tag_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tag_ids)\
                                            .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                            .order_by('-same_tags', '-time_published')[:4]

    return render(request, 
                'blog/post/detail.html', 
                {'post': post,
                'comments': comments,
                'new_comment': new_comment,
                'comment_form': comment_form,
                'similar_posts': similar_posts})


def post_share_view(request, post_id):
    # retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # if form is submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # if form passes validation, clean the data
            clean = form.cleaned_data
            # send mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{clean['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n \n"\
                f"{clean['name']}\'s comments: {clean['comment']}"
            send_mail(subject, message, 'rainfidelis@gmail.com', [clean['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 
                  'blog/post/share.html', 
                  {'post':post, 
                  'form':form, 
                  'sent':sent})


def post_search_view(request):

    start_time = time.time()

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            search_rank = SearchRank(search_vector, search_query)
            query_time = f"{(time.time() - start_time)//1000} seconds"
            results = Post.published.annotate(
                search=search_vector, rank=search_rank
                ).filter(search=search_query).order_by('-rank')
            # results = Post.published.annotate(
            #     similarity = TrigramSimilarity('title', 'query'),
            #     ).filter(similarity__gt=0.1).order_by('-similarity')

    else:
        form = SearchForm()
        query = None
        results = []

    return render(request, 
                  'blog/post/search.html', 
                  {'form':form, 
                   'query':query,
                   'query_time':query_time, 
                   'results':results})