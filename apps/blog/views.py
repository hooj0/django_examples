from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Post, Tags


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'latest_blog_list'

    def get_queryset(self):
        return Post.objects.order_by('-published_date')[:5]

class DetailView(generic.DetailView):
    model = Post
    template_name = 'blog/detail.html'

class TagsView(generic.DetailView):
    model = Post
    template_name = 'blog/tags.html'

def make_tags(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    Tags.objects.create(post=post, tag_name=request.POST["tag_name"])

    return HttpResponseRedirect(reverse("blog:tags", args=(post.id, )))