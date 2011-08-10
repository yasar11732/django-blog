from feeds import LatestPosts, TagFeed
from sitemaps import PostSitemap, TagSitemap, HomePageSitemap
from django.conf.urls.defaults import patterns
from portal.blog.views import common_data
from portal.blog.models import Post

sitemaps = {
'posts' : PostSitemap,
'tags' : TagSitemap,
'homepage' : HomePageSitemap
}

urlpatterns = patterns('django.views.generic.date_based',
    (r'^$','arhive_index',{
        'template_name': 'blog/index.html', 
        'queryset' : Post.objects.filter(yayinlandi=True),
        'num_latest' : 10,
        'extra_context' : common_data
        }),
)
urlpatterns += patterns('portal.blog.views',
	(r'^$', 'home'),
	(r'^post/(?P<slug>[^/]+)/$','post'),
    (r'^tag/(?P<tag>[^/]+)/$','tag'),
    (r'^tag/$','tag_index'),
)

urlpatterns += patterns('',
	(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps' : sitemaps}),
	(r'^rss/$', LatestPosts()),
	(r'^tag/(?P<tag>[^/]+)/rss/$', TagFeed()),
)   