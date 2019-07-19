from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image


# Create your models here.
class ArticleColumn(models.Model):
    """
    栏目的model
    """
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    # 文章作者，参数on_delete用于指定数据删除的方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章标题，models.CharField为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100)
    # 文章正文，保存大量文本使用TextField
    body = models.TextField()
    # 文章创建时间，参数default=timezone.now指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)
    # 文章更新时间，参数auto_now=True指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    # 浏览量
    total_views = models.PositiveIntegerField(default=0)

    column = models.ForeignKey(ArticleColumn, null=True, blank=True, on_delete=models.CASCADE, related_name='article')
    tags = TaggableManager(blank=True)
    avatar = models.ImageField(upload_to='article/%Y%m%d', blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        article = super(ArticlePost, self).save(force_insert, force_update, using, update_fields)
        if self.avatar and not update_fields:
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article

    class Meta:
        # ordering 指定模型返回的数据的排列顺序
        # -created 表明数据倒序排列
        ordering = ('-created',)

    def __str__(self):
        return self.title

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    def was_created_recently(self):
        diff = timezone.now() - self.created
        if diff.days <= 0 and diff.seconds < 60:
            return True
        else:
            return False

