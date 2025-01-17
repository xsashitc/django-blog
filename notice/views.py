from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from article.models import ArticlePost


# Create your views here.

class CommentNoticeListView(LoginRequiredMixin, ListView):
    """通知列表"""
    # 上下文列表
    context_object_name = "notices"
    # 模板位置
    template_name = "notice/list.html"
    # 登录重定向
    login_url = "/userprofile/login"

    def get_queryset(self):
        return self.request.user.notifications.unread()


class CommentNoticeUpdateView(View):
    """更新通知状态"""
    # 处理get请求
    def get(self, request):
        # 获取未读信息
        notice_id = request.GET.get('notice_id')
        if notice_id:
            article = ArticlePost.objects.get(id=request.GET.get('article_id'))
            request.user.notifications.get(id=notice_id).mark_as_read()
            return redirect(article)
        else:
            request.user.notifications.mark_all_as_read()
            return redirect('notice:list')
