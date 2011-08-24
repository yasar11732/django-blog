# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.sitemaps import ping_google
from django.core.validators import validate_slug
# Create your models here.



class Tag(models.Model):
    text = models.CharField(max_length=15, unique=True)
    slug = models.SlugField(blank=True)
    created = models.DateTimeField(default=datetime.now)
    
    def __unicode__(self):
        return self.text
        
    def get_absolute_url(self):
        return "/tag/%s/" % self.text

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    abstract = models.TextField(max_length=500)
    post = models.TextField()
    pub_date = models.DateTimeField("Date Published", default=datetime.now)
    last_mod = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag,blank=True)
    yayinlandi = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.title
        
    def get_absolute_url(self):
        return "/post/%s/" % self.slug
        
    def yayinlandi_mi(self):
        return self.yayinlandi and u"evet" or u"hayır"
        
    def save(self,force_insert=False, force_update=False,using=None):
        super(Post, self).save(force_insert, force_update,using=using)
        if self.yayinlandi:
            try:
                ping_google('/sitemap.xml')
            except:
                pass

class Message(models.Model):
    post = models.ForeignKey(Post)
    message = models.CharField(max_length=500)
    email = models.EmailField(blank=True)
    
    def __unicode__(self):
        return self.message
