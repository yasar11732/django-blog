from portal.blog.models import Post, Tag, Setting
from django.template.defaultfilters import slugify
from django.contrib import admin
from datetime import datetime


class PostAdmin(admin.ModelAdmin):
    readonly_fields = ("slug","last_mod","pub_date")
	prepopulated_fields = {"slug": ("title",)}
    
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
        
        


admin.site.register(Post,PostAdmin)
admin.site.register(Tag)
admin.site.register(Setting)