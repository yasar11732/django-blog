# -*- coding:utf-8 -*-
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from blog.models import Post, Tag

from django.core import urlresolvers

class lazy_string(object):
    def __init__(self, function, *args, **kwargs):
        self.function=function
        self.args=args
        self.kwargs=kwargs
        
    def __str__(self):
        if not hasattr(self, 'str'):
            self.str=self.function(*self.args, **self.kwargs)
        return self.str

def reverse(*args, **kwargs):
    return lazy_string(urlresolvers.reverse, *args, **kwargs)

class LatestPosts(Feed):
    title = u"yasar11732: En Son Yazılar"
    link = reverse("blog.views.homepage")
    description = u"Yeni yazıların güncellemeleri"

    def items(self):
        return Post.objects.filter(yayinlandi=True).order_by("-pub_date")[:5]

    def item_title(self,item):
        return item.title

    def item_description(self,item):
        return item.abstract
    
    def item_pubdate(self,item):
        return item.pub_date
        
    def item_link(self,item):
        return reverse('blog.views.post',args=[post.slug])

class TagFeed(Feed):

    def get_object(self,request,tag):
        return get_object_or_404(Tag, slug=tag)

    def title(self,obj):

        return u"yasar11732: %s ile ilgili makaleler" % obj.text
    
    def item_description(self,obj):
        return obj.abstract

    def link(self,obj):
        return reverse("tag",args=[obj.slug])
    
    def description(self, obj):
        return u"%s ile ilgili tüm yazılar" % obj.text

    def items(self,obj):

        return obj.post_set.filter(yayinlandi=True).order_by("-pub_date")[:15]
    
    def item_pubdate(self,item):
        return item.pub_date
        
    def item_link(self,item):
        return reverse("blog.views.post",arg=[item.slug])
