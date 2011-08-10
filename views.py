# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from portal.blog.models import Post, Tag, Setting
from django.template import RequestContext
from django.core.urlresolvers import reverse


blog_baslik = Setting.objects.filter(anahtar="blog_baslik")
if len(blog_baslik) == 1:
    blog_baslik = blog_baslik[0].deger
else:
    blog_baslik = ""
blog_slogan = Setting.objects.filter(anahtar="blog_slogan")
if len(blog_slogan) == 1:
    blog_slogan = blog_slogan[0].deger
else:
    blog_slogan = ""

common_data = {'slogan': blog_slogan,
     'blog_name' :  blog_baslik,
         }
def home(request):
    global common_data
    latest_posts = Post.objects.filter(yayinlandi=True).order_by('-pub_date')[:10]
    datas = {'latest_posts': latest_posts,
                 'rss_link': "/rss/" 
        
    }
    datas.update(common_data)
    return render_to_response('blog/index.html',datas)
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

def tag_index(request):
    datas = {'tags' : Tag.objects.all()}
    datas.update(common_data)
    return render_to_response('blog/tag_index.html', datas)