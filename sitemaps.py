from django.contrib.sitemaps import Sitemap
from portal.blog.models import Post, Tag

class HomePage:
    def get_absolute_url(self):
        return "/"

class HomePageSitemap(Sitemap):
    changefreq = "daily"
    priority = "1"
    
    def items(self):
        return [HomePage(),]
    
    def lastmod(self,obj):
        return Post.objects.filter(yayinlandi=True).order_by("-pub_date")[0].pub_date

class PostSitemap(Sitemap):
	changefreq = "never"
	priority = 0.5
	
	def items(self):
		return Post.objects.filter(yayinlandi=True)
	
	def lastmod(self,obj):
		return obj.pub_date
		
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