from django.db import models
from datetime import datetime
from django.contrib.sitemaps import ping_google
from django.core.validators import validate_slug
# Create your models here.

class Setting(models.Model):
    anahtar = models.CharField(max_length=20,unique=True)
    deger = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.anahtar
        
class Tag(models.Model):
    text = models.CharField(max_length=15, unique=True, validators = [validate_slug])
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
    tags = models.ManyToManyField(Tag)
    yayinlandi = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.slug
        
    def get_absolute_url(self):
        return "/post/%s/" % self.slug
        
    def save(self,force_insert=False, force_update=False):
        super(Post, self).save(force_insert, force_update)
        if self.yayinlandi:
            try:
                ping_google('/sitemap.xml')
            except:
                pass
        
        
