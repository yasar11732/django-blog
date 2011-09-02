# Create your views here.
from django.conf import settings
from django.contrib.sites.models import Site
import urllib2
import json
from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404, HttpResponseNotFound
from django.views.decorators.http import condition, require_http_methods
from django.views.decorators.gzip import gzip_page
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response, get_object_or_404
from blog.models import Post, Tag, Message
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from time import time
from django.db.models import Count
import re

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

common_data = {
    'slogan': settings.BLOG_SLOGAN,
    'blog_name' :  settings.BLOG_TITLE,
    'domain' :  Site.objects.get(id=settings.SITE_ID).domain,
    'STATIC_URL' : settings.STATIC_URL,
    'protocol' : "http",
    }

def latest_post(request):
    return Post.objects.filter(yayinlandi=True).latest("pub_date").pub_date
    
def last_modified(request,slug):
    try:
        post = Post.objects.get(slug=slug)
        return post.last_mod
    # Doing this instead of 404
    # in order to not to break suggestions!
    except Post.DoesNotExist:
        return None
    
def tag_last_modified(request,tag):
    try:
        tag = Tag.objects.get(text=Tag)
    except Tag.DoesNotExist:
        return None
    return tag.post_set.filter(yayinlandi=True).latest("pub_date").pub_date

def last_tag(request):
    return Tag.objects.all().latest("created").created

def handlenotfound(request,suggestions = None):
    global common_data
    datas = {
        'tags' : Tag.objects.all(),
        'date_list' : Post.objects.filter(yayinlandi=True).dates("pub_date","year")
    }
    if suggestions is not None:
        datas["suggestions"] = suggestions
    template = loader.get_template("blog_404.html")
    datas.update(common_data)
    icerik = Context(datas)
    
    return HttpResponseNotFound(template.render(icerik))
    
def handleServerError(request):
    return render_to_response("blog_500.html",Context())

@require_http_methods(["POST"])
def message(request):
    try:
        if int(time()) - request.session["last_message"] < 10:
            return HttpResponse("4")
    except:
        pass
    slug = request.POST["post"]
    message = request.POST["message"]
    
    try:
        p = Post.objects.get(slug=slug)
    except:
        p = None
    
    valid_message = False
    try:
        email = request.POST["email"]
    except:
        email = ""
    if email != "":
        if not re.match("^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$",email):
            return HttpResponse("5")
    if len(message) <= 500 and len(message) >= 5:
        valid_message = True
    if p is None and valid_message is False:
        return HttpResponse("3")
    elif p is None:
        return HttpResponse("1")
    elif valid_message is False:
        return HttpResponse("2")
    
    mes = Message.objects.create(post=p,message=request.POST['message'],email=email)
    request.session["last_message"] = int(time())
    return HttpResponse("0")

@condition(last_modified_func=latest_post)
@gzip_page
@cache_page(900)
def homepage(request):
    global common_data
    query_set = Post.objects.filter(yayinlandi=True)
    latest = []
    for post in query_set.order_by("-pub_date")[:10]:
        latest.append((post,post.tags.all()))
    datas = {
        'latest' : latest,
        'date_list' : query_set.dates("pub_date","year"),
        'etiket_listesi' : Tag.objects.annotate(post_sayisi=Count('post')).order_by("-post_sayisi")[:10]
    }
    datas.update(common_data)
    return render_to_response("blog_index.html",datas)
@condition(last_modified_func=latest_post)
@gzip_page
@cache_page(900)
def post_index(request):
    global common_data
    datas = {
        'latest' : Post.objects.filter(yayinlandi=True).order_by("-pub_date")[:30],
        'date_list' : Post.objects.filter(yayinlandi=True).dates("pub_date","year"),
    }
    datas.update(common_data)
    return render_to_response("blog_post_index.html",datas)
    
@gzip_page
@cache_page(900)
def arsiv_index(request):
    global common_data
    datas = {
        'date_list' : Post.objects.filter(yayinlandi=True).dates("pub_date","year")
    }
    datas.update(common_data)
    return render_to_response("blog_arsiv_index.html",datas)
@condition(last_modified_func=last_modified)
@gzip_page
@cache_page(900)
def post(request,slug):
    global common_data
    from django.core.mail import mail_admins
    try:
        p = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        suggestions = suggest(slug, [p.slug for p in Post.objects.filter(yayinlandi=True)])
        if len(suggestions) == 0:
            raise Http404
        elif len(suggestions) == 1:
            p = Post.objects.get(slug = suggestions[0])
            return HttpResponsePermanentRedirect(p.get_absolute_url())
        else:
            posts = [Post.objects.get(slug=suggestion) for suggestion in suggestions]
            suggestions = [p.get_absolute_url() for p in posts]
            return handlenotfound(request,suggestions)
        
    if p.yayinlandi or request.user.is_authenticated():
        datas = {
                'post': p,
                'tags' : p.tags.all(),
                'messages' : settings.BLOG_MESSAGES_ENABLED,
                }
        datas.update(common_data)
        try:
            abs_url = common_data["protocol"] + "://" + common_data["domain"] + str(p.get_absolute_url())
            request_line = '{"longUrl" : "' + abs_url + '"}'
            request = urllib2.Request("https://www.googleapis.com/urlshortener/v1/url",data=request_line,headers={"Content-Type" : "application/json"})
            socket = urllib2.urlopen(request)
            response = socket.read()
            socket.close()
            jdict = json.loads(response)
            datas["shorturl"] = jdict["id"]
        except:
            import traceback
            import StringIO
            
            
            mail_admins("url shortage error",traceback.format_exc())
        mail_admins("your data!",datas)    

        return render_to_response('blog_post.html', datas, context_instance=RequestContext(request))
    else:
        raise Http404

@condition(last_modified_func=tag_last_modified)
@gzip_page
@cache_page(900)
def tag(request,tag):
    global common_data
    try:
        tag = Tag.objects.get(slug=tag)
    except Tag.DoesNotExist:
        suggestions = suggest(tag, [t.slug for t in Tag.objects.all()])
        if len(suggestions) <= 0:
            raise Http404
        elif len(suggestions) == 1:
            t = Tag.objects.get(slug = suggestions[0])
            return HttpResponsePermanentRedirect(reverse("tag",args=[t.slug]))
        else:
            tags = [ Tag.objects.get(slug=suggestion) for suggestion in suggestions ]
            suggestions = [reverse("tag",args=[tag.slug]) for tag in tags]
            return handlenotfound(request,suggestions)
    post_set = tag.post_set.filter(yayinlandi=True).order_by("-pub_date")
    datas = {
            'tag' : tag,
            'latest_posts': post_set,
            }
    datas.update(common_data)
    return render_to_response('blog_tag.html', datas)

@condition(last_modified_func=last_tag)
@gzip_page
@cache_page(900)
def tag_index(request):
    datas = {'tags' : Tag.objects.all()}
    datas.update(common_data)
    return render_to_response('blog_tag_index.html', datas)
