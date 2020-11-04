import pdb

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import strip_tags
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from main.forms import EmailPostForm, CommentForm
from main.models import Post, Category, Comment
from main.views import prepare_context


class PostListView(ListView):
    model = Post
    paginate_by = 10
    queryset = Post.published.all().order_by('-date_upd')
    context_object_name = 'posts'
    template_name = 'post/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        context['categories'] = Category.objects.all()[:4]
        return context


class PostView(TemplateView):
    template_name = 'post/detail.html'
    paginate_by = 8

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        context['categories'] = Category.objects.all()[:4]
        context['posts'] = Post.objects.all()[:self.paginate_by]
        try:
            if 'pk' in self.kwargs:
                context['model'] = Post.objects.get(pk=self.kwargs.get('pk'))
                context['comments'] = Comment.objects.filter(post_id=context['model'])[:self.paginate_by]
            context['models'] = Post.objects.all()[:self.paginate_by]
        except Post.DoesNotExist:
            context['models'] = Post.objects.all()[:self.paginate_by]
        return context

    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = self.get_context_data(**kwargs)
        data = request.POST.copy()
        if request.user.is_authenticated:
            data['owner'] = request.user
        if pk is not None:
            context['model'] = Post.objects.get(pk=pk)
            data['post_id'] = context['model']
            form = CommentForm(initial=data, user=request.user, post=context['model'], data=data)
        else:
            return redirect('main:post_list')
            # form = CommentForm(initial=data, user=request.user, data=data)

        content = strip_tags(request.POST.get('content', None))
        if form.is_valid() and content is not None and isinstance(content, str) and len(content.strip()) > 0:
            form.content = content
            obj = form.save(commit=False)
            obj.save()
            return redirect('main:post_list')
        context['form'] = form
        return render(request, template_name=self.template_name, context=context)
        # return redirect('main:post_detail', pk=pk)

    def get(self, request, pk, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if pk is not None:
            context['model'] = Post.objects.get(pk=pk)
            form = CommentForm(user=request.user, post=context['model'])
        else:
            return redirect('main:post_list')
        # Create Comment object but don't save to database yet
        context['form'] = form
        return render(request, template_name=self.template_name, context=context)


def post_share(request, pk):
    post = get_object_or_404(Post, pk=pk)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            # send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'post/share.html', {'post': post, 'form': form, 'sent': sent})
