from feeds import LatestPosts, TagFeed
from sitemaps import PostSitemap, TagSitemap, HomePageSitemap
from django.conf.urls.defaults import *
from blog.views import common_data
from blog.models import Post

sitemaps = {
'posts' : PostSitemap,
'tags' : TagSitemap,
'homepage' : HomePageSitemap
}

urlpatterns = patterns('django.views.generic.date_based',
    url(r'^arsiv/(?P<year>\d{4})/$','archive_year',{
            'template_name' : 'blog/yillar.html',
            'date_field' : 'pub_date',
            'queryset' : Post.objects.filter(yayinlandi=True),
            'extra_context' : common_data,
            'make_object_list' : True,
            'template_object_name' : 'makale'
    }, name="arsiv_year"),
    
    url(r'^arsiv/(?P<year>\d{4})/(?P<month>\d{1,2})/$','archive_month',{
            'template_name' : 'blog/ay.html',
            'date_field' : 'pub_date',
            'queryset' : Post.objects.filter(yayinlandi=True),
            'extra_context' : common_data,
            'template_object_name' : 'makale',
            'month_format' : "%m",
    },name="arsiv_month"),
)
urlpatterns += patterns('blog.views',
    (r'^$','homepage'),
    (r'^post/$','post_index'),
    (r'^arsiv/$','arsiv_index'),
	url(r'^post/(?P<slug>[^/]+)/$','post',name="post"),
    url(r'^tag/(?P<tag>[^/]+)/$','tag',name="tag"),
    url(r'^tag/$','tag_index',name="tag_index"),
    (r'^message$','message')
)

urlpatterns += patterns('',
	(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps' : sitemaps}),
	url(r'^rss/$', LatestPosts(),name="rss"),
	url(r'^tag/(?P<tag>[^/]+)/rss/$', TagFeed(),name="tag_rss"),
)   
