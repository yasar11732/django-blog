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
    (r'^arsiv/(?P<year>\d{4})/$','archive_year',{
            'template_name' : 'blog/yillar.html',
            'date_field' : 'pub_date',
            'queryset' : Post.objects.filter(yayinlandi=True),
            'extra_context' : common_data,
            'make_object_list' : True,
            'template_object_name' : 'makale'
    }),
    
    (r'^arsiv/(?P<year>\d{4})/(?P<month>\d{1,2})/$','archive_month',{
            'template_name' : 'blog/ay.html',
            'date_field' : 'pub_date',
            'queryset' : Post.objects.filter(yayinlandi=True),
            'extra_context' : common_data,
            'template_object_name' : 'makale',
            'month_format' : "%m",
    }),
)
urlpatterns += patterns('portal.blog.views',
    (r'^$','homepage'),
    (r'^post/$','post_index'),
    (r'^arsiv/$','arsiv_index'),
	(r'^post/(?P<slug>[^/]+)/$','post'),
    (r'^tag/(?P<tag>[^/]+)/$','tag'),
    (r'^tag/$','tag_index'),
)

urlpatterns += patterns('',
	(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps' : sitemaps}),
	(r'^rss/$', LatestPosts()),
	(r'^tag/(?P<tag>[^/]+)/rss/$', TagFeed()),
)   
