from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost, ArticleColumn
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm


# Create your views here.

def article_list(request):
    search = request.GET.get("search")
    order = request.GET.get("order")
    column = request.GET.get("column")
    tag = request.GET.get("tag")
    article_list = ArticlePost.objects.all()
    if search:
        # if order == 'total_views':
        #     article_list = ArticlePost.objects.filter(
        #         Q(title__icontains=search) | Q(body__icontains=search)
        #     ).order_by('-total_views')
        # else:
        #     article_list = ArticlePost.objects.filter(
        #         Q(title__icontains=search) | Q(body__icontains=search)
        #     )
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''
        # if order == 'total_views':
        #     article_list = ArticlePost.objects.all().order_by('-total_views')
        # else:
        #     article_list = ArticlePost.objects.all()
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {'articles': articles, 'order': order, 'search': search, 'column': column, 'tag': tag}
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(extensions=[
        #  包含表格、缩写等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        # 目录扩展
        'markdown.extensions.toc',
    ])
    article.body = md.convert(article.body)
    comments = Comment.objects.filter(article=id)
    comment_form = CommentForm()

    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id')
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id')
    if pre_article.count() > 0:
        pre_article = pre_article[0]
    else:
        pre_article = None
    if next_article.count() > 0:
        next_article = next_article[0]
    else:
        next_article = None
    context = {'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form, 'pre_article': pre_article, 'next_article': next_article}
    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不存到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中id=1的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将数据存到数据库中
            new_article.save()
            # 保存tags的多对多关系
            article_post_form.save_m2m()
            return redirect("article:article_list")
        # 数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写")
    # 如果用户请求获取数据
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse('抱歉，你无权删除这篇文章')
    article.delete()
    return redirect("article:article_list")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新title、body等字段
    GET方法进入初始表单页面
    :param request:
    :param id: 文章的id
    :return:
    """
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse('抱歉，你无权修改这篇文章')
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect('article:article_detail', id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article': article, 'articlePostForm': article_post_form, 'columns': columns,
                   'tags': ','.join([x for x in article.tags.names()])}
        return render(request, 'article/update.html', context)
