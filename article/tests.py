from django.test import TestCase

import datetime
from django.utils import timezone
from article.models import ArticlePost
from django.contrib.auth.models import User


# Create your tests here.

class ArticlePostModelTests(TestCase):

    def test_was_created_recently_with_future_article(self):
        author = User.objects.all().filter(id=6)

        future_article = ArticlePost(author=author, title='test', body='test',
                                     created=timezone.now() + datetime.timedelta(days=30))
        self.assertIs(future_article.was_created_recently(), False)
