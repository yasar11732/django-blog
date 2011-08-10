from feeds import LatestPosts, TagFeed
from sitemaps import PostSitemap, TagSitemap, HomePageSitemap
from django.conf.urls.defaults import patterns

sitemaps = {
'posts' : PostSitemap,
'tags' : TagSitemap,
'homepage' : HomePageSitemap
}

urlpatterns = patterns('portal.blog.views',
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