# -*- coding:utf-8 -*-
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from portal.blog.models import Post, Tag

class LatestPosts(Feed):
    title = "yasar11732: En Son Yazılar"
    link = "/"
    description = "Yeni yazilarin güncellemeleri"

    def items(self):
        return Post.objects.filter(yayinlandi=True).order_by("-pub_date")[:5]

    def item_title(self,item):
        return item.title

    def item_description(self,item):
        return item.abstract
    def item_pubdate(self,item):
        return item.pub_date

class TagFeed(Feed):

    def get_object(self,request,tag):
        return get_object_or_404(Tag, text=tag)

    def title(self,obj):

        return "yasar11732: %s ile ilgili makaleler" % obj.text
    def item_description(self,obj):
        return obj.abstract

    def link(self,obj):
        return "/tag/%s/" % obj.text
    
    def description(self, obj):
        return "%s ile ilgili tum yazilar" % obj.text

    def items(self,obj):

        return obj.post_set.filter(yayinlandi=True).order_by("-pub_date")[:15]
    
    def item_pubdate(self,item):
        return item.pub_date
