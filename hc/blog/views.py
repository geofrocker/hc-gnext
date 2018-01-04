from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import generic
from .forms import CategoryForm, PostForm
from .models import Category, Post


class BlogIndexView(generic.TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(BlogIndexView, self).get_context_data(**kwargs)
        ctx['posts'] = Post.objects.all()
        return ctx


class CreateCategoryView(generic.CreateView):
    form_class = CategoryForm
    template_name = 'blog/post_form.html'

    def get_success_url(self):
        return reverse('hc-blog:category-create')

    def get_context_data(self, **kwargs):
        ctx = super(CreateCategoryView, self).get_context_data(**kwargs)
        post_form = PostForm()
        categories = Category.objects.all()
        ctx['categories'] = categories
        ctx['post_form'] = post_form
        ctx['page_action'] = 'create'
        return ctx


class CreateBlogPostView(generic.CreateView):
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def get_success_url(self):
        return reverse('hc-blog:index')

    def get(self, request, *args, **kwargs):
        super(CreateBlogPostView, self).get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('hc-blog:category-create'))

    def get_form_kwargs(self):
        kwargs = super(CreateBlogPostView, self).get_form_kwargs()
        if not 'request' in kwargs:
            kwargs.update({'request': self.request})

        return kwargs


class RetrievePostDetailView(generic.DetailView):
    model = Post


class UpdatePostView(generic.UpdateView):
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse('hc-blog:post-detail', kwargs={'slug': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super(UpdatePostView, self).get_form_kwargs()
        if 'request' not in kwargs:
            kwargs.update({'request': self.request})

        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(UpdatePostView, self).get_context_data(**kwargs)
        ctx['page_action'] = 'update'
        ctx['category_form'] = CategoryForm()
        return ctx


class DeletePostView(generic.DeleteView):
    model = Post

    def post(self, request, *args, **kwargs):
        post_data = request.POST
        confirm = post_data.get('confirm', False)

        if confirm != 'on' or not confirm:
            return HttpResponseRedirect(
                reverse('hc-blog:post-detail', kwargs={'slug': kwargs.get('slug', '')}))

        return super(DeletePostView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('hc-blog:index')