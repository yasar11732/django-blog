from django.contrib.sitemaps import Sitemap
from blog.models import Post, Tag
from django.utils.functional import lazy
from django.core import urlresolvers

    
reverse = lazy(urlresolvers.reverse, str)

class HomePage:
    def get_absolute_url(self):
        return reverse("blog.views.homepage")

class HomePageSitemap(Sitemap):
    changefreq = "daily"
    priority = "1"
    
    def items(self):
        return [HomePage()]
    
    def lastmod(self,obj):
        return Post.objects.filter(yayinlandi=True).order_by("-pub_date")[0].pub_date

class PostSitemap(Sitemap):
	changefreq = "never"
	priority = 0.5
	
	def items(self):
		return Post.objects.filter(yayinlandi=True)
	
	def lastmod(self,obj):
		return obj.last_mod
		
class TagSitemap(Sitemap):
	
	changefreq = "weekly"
	priority = "0.4"
	
	def items(self):
		return Tag.objects.all()
	
	def lastmod(self,obj):
		posts =  obj.post_set.all().order_by('-pub_date')
		if len(posts) > 0:
			return posts[0].pub_date
		else:
			return None