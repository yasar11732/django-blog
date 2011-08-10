from portal.blog.models import Post, Tag, Setting
from django.contrib import admin


class PostAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post,PostAdmin)
admin.site.register(Tag)
admin.site.register(Setting)