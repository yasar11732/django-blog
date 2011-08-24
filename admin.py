# -*- coding:utf-8 -*-
from blog.models import Post, Tag, Message
from django.template.defaultfilters import slugify
from django.contrib import admin
from datetime import datetime

# To handle turkish characters better!

class PostAdmin(admin.ModelAdmin):
    readonly_fields = ("slug","last_mod","pub_date")
    fieldsets = [
        (None     , { "fields" : ["title","abstract","post","tags","yayinlandi"]}),
        ("Details", { "fields" : ["pub_date","last_mod","slug"], "classes" : ["collapse"]})
    
    ]
    
    list_display = ("title","pub_date","last_mod","yayinlandi_mi")
    list_filter = ['pub_date']
    search_fields = ["title","abstract","post"]
    date_hierarchy = 'pub_date'
    
    
    def save_model(self,request,obj,form,change):
        if obj.slug == "" or obj.slug is None:
            obj.slug = slugify(obj.title)
        # I get database representation of the object to check if
        # it was not published before and it is published now
        # in order to set pub_date right
        
        if change is True:
            obj_db = Post.objects.get(pk=obj.id)
            if obj_db.yayinlandi == False and obj.yayinlandi == True:
                obj.pub_date = datetime.now()
        
        obj.save()
        

    
class messageAdmin(admin.ModelAdmin):
    readonly_fields = ["post","message","email"]
    fields = ["post","message","email"]
    def has_add_permission(*args,**kwargs):
        return False
        
class TagAdmin(admin.ModelAdmin):
    
    readonly_fields = ("slug",)
    
    def save_model(self,request,obj,form,change):
        if obj.slug == "" or obj.slug is None:
            obj.slug = slugify(obj.text)
    
        obj.save()

admin.site.register(Post,PostAdmin)
admin.site.register(Tag,TagAdmin)
admin.site.register(Message,messageAdmin)
