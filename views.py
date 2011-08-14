# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404, HttpResponseNotFound
from django.views.decorators.http import condition
from django.views.decorators.gzip import gzip_page
from django.shortcuts import render_to_response, get_object_or_404
from portal.blog.models import Post, Tag, Setting
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse

alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789-'
# Stolen from http://norvig.com/spell-correct.html
def suggest(word,Nwords):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   all_suggestions = set(deletes + transposes + replaces + inserts)
   return [suggestion for suggestion in all_suggestions if suggestion in Nwords]
   
try:
    blog_baslik = Setting.objects.get(anahtar="blog_baslik").deger
except:
    blog_baslik = ""
try:
    blog_slogan = Setting.objects.get(anahtar="blog_slogan").deger
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

def handlenotfound(request,suggestions = None):
    global common_data
    datas = {
        'tags' : Tag.objects.all(),
        'date_list' : Post.objects.filter(yayinlandi=True).dates("pub_date","year")
    }
    if suggestions:
        datas["suggestions"] = suggestions
    template = loader.get_template("404.html")
    datas.update(common_data)
    icerik = Context(datas)
    
    return HttpResponseNotFound(template.render(icerik))

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
@condition(last_modified_func=latest_post)
@gzip_page
def post_index(request):
    global common_data
    datas = {
        'latest' : Post.objects.filter(yayinlandi=True).order_by("-pub_date")[:30],
        'date_list' : Post.objects.filter(yayinlandi=True).dates("pub_date","year"),
    }
    datas.update(common_data)
    return render_to_response("blog/post_index.html",datas)
    
@gzip_page
def arsiv_index(request):
    global common_data
    datas = {
        'date_list' : Post.objects.filter(yayinlandi=True).dates("pub_date","year")
    }
    datas.update(common_data)
    return render_to_response("blog/arsiv_index.html",datas)
@condition(last_modified_func=last_modified)
@gzip_page
def post(request,slug):
    global common_data
    try:
        p = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        suggestions = suggest(slug, [p.slug for p in Post.objects.filter(yayinlandi=True)])
        if len(suggestions) == 0:
            raise Http404
        elif len(suggestions) == 1:
            p = Post.objects.get(slug = suggestion[0])
            return HttpResponsePermanentRedirect(p.get_absolute_url())
        else:
            suggestions = [p.get_absolute_url() for p in Post.objects.get(slug=suggestion) for suggestion in suggestions]
            return handlenotfound(request,suggestions)
        
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
    try:
        tag = Tag.objects.get(text=tag)
    except Tag.DoesNotExist:
        suggestions = suggest(tag, [t.text for t in Tag.objects.all()])
        if len(suggestions) <= 0:
            raise Http404
        elif len(suggestions) == 1:
            t = Tag.objects.get(text = suggestion[0])
            return HttpResponsePermanentRedirect(t.get_absolute_url())
        else:
            suggestions = [t.get_absolute_url() for t in Tag.objects.get(text=suggestion) for suggestion in suggestions]
            return handlenotfound(request,suggestions)
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
