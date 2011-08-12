# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import condition
from django.views.decorators.gzip import gzip_page
from django.shortcuts import render_to_response, get_object_or_404
from portal.blog.models import Post, Tag, Setting
from django.template import RequestContext
from django.core.urlresolvers import reverse


try:
    blog_baslik = Setting.objects.get(anahtar="blog_baslik")
except:
    blog_baslik = ""
try:
    blog_slogan = Setting.objects.get(anahtar="blog_slogan")
except:
    blog_slogan = ""

common_data = {'slogan': blog_slogan,
     'blog_name' :  blog_baslik,
         }

def latest_post(request):
    return Post.objects.filter(yayinlandi=True).latest("pub_date").pub_date
    
def last_modified(request,slug):
    return get_object_or_404(Post,slug=slug).last_mod
    
def tag_last_modified(request,tag):
    return get_object_or_404(Tag,text=tag).post_set.filter(yayinlandi=True).latest("pub_date").pub_date

def last_tag(request):
    return Tag.objects.all().latest("created").created
   
@condition(last_modified_func=latest_post)
@gzip_page
def homepage(request):
    global common_data
    query_set = Post.objects.filter(yayinlandi=True)
    datas = {
        'latest' : query_set.order_by("-pub_date")[:10],
        'date_list' : query_set.dates("pub_date","year"),
    }
    datas.update(common_data)
    return render_to_response("blog/index.html",datas)
    
@condition(last_modified_func=last_modified)
@gzip_page
def post(request,slug):
    global common_data
    p = get_object_or_404(Post, slug=slug)
    if p.yayinlandi or request.user.is_authenticated():
        datas = {
                'post': p,
                'tags' : p.tags.all(),
                }
        datas.update(common_data)
        return render_to_response('blog/post.html', datas, context_instance=RequestContext(request))
    else:
        raise Http404

@condition(last_modified_func=tag_last_modified)
@gzip_page 
def tag(request,tag):
    global common_data
    tag = get_object_or_404(Tag, text=tag)
    post_set = tag.post_set.filter(yayinlandi=True).order_by("-pub_date")
    datas = {
            'tag' : tag,
            'latest_posts': post_set,
            }
    datas.update(common_data)
    return render_to_response('blog/tag.html', datas)

@condition(last_modified_func=last_tag)
@gzip_page
def tag_index(request):
    datas = {'tags' : Tag.objects.all()}
    datas.update(common_data)
    return render_to_response('blog/tag_index.html', datas)
