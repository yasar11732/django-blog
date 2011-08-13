# -*- coding:utf-8 -*-
from portal.blog.models import Post, Tag, Setting
from django.template.defaultfilters import slugify
from django.contrib import admin
from datetime import datetime

# To handle turkish characters better!
def my_slugify(text):
    change_characters = {
        u"ı" : u"i",
        u"İ" : u"i",
        u"ğ" : u"ğ",
        u"Ğ" : u"Ğ",
        u"ü" : u"u",
        u"Ü" : u"U",
        u"ş" : u"s",
        u"Ş" : u"S",
        u"ö" : u"o",
        u"Ö" : u"O",
        u"ç" : u"c",
        u"Ç" : u"C"
        
    }
    
    for k, v in change_characters.items():
        text.replace(k,v)
    return slugify(text)


class PostAdmin(admin.ModelAdmin):
    readonly_fields = ("slug","last_mod","pub_date")
    
    def save_model(self,request,obj,form,change):
        if obj.slug == "" or obj.slug is None:
            obj.slug = my_slugify(obj.title)
 
        # I get database representation of the object to check if
        # it was not published before and it is published now
        # in order to set pub_date right
        
        if change is True:
            obj_db = Post.objects.get(pk=obj.id)
            if obj_db.yayinlandi == False and obj.yayinlandi == True:
                obj.pub_date = datetime.now()
        
        obj.save()
        
        


admin.site.register(Post,PostAdmin)
admin.site.register(Tag)
admin.site.register(Setting)