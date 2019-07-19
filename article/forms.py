from django import forms
from .models import ArticlePost


class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指定数据类型来源
        model = ArticlePost
        fields = ('title', 'body', 'tags', 'avatar')
