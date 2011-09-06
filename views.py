import urllib2
import json
import re
from time import time

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.http import Http404, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.views.decorators.gzip import gzip_page
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response, get_object_or_404
from blog.models import Post, Tag, Message, ShortUrl
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.mail import mail_admins
from django.db.models import Count


alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789-'
# Stolen from http://norvig.com/spell-correct.html
def suggest(word,Nwords):
    """Tries to corrrect 1-edit spelling errors
    
    returns list of strings"""
    
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    all_suggestions = set(deletes + transposes + replaces + inserts)
    
    return [
        suggestion for suggestion in all_suggestions 
        if suggestion in Nwords
    ]

common_data = {
    'slogan': settings.BLOG_SLOGAN,
    'blog_name' :  settings.BLOG_TITLE,
    'domain' :  Site.objects.get(id=settings.SITE_ID).domain,
    'STATIC_URL' : settings.STATIC_URL,
    'protocol' : "http",
    }
    
def getShortUrl(Url):
    "Shortens url and returns it as string."
    try:
        return ShortUrl.objects.get(longUrl=Url).shortUrl
    except ShortUrl.DoesNotExist:
        request_line = '{"longUrl" : "' + Url + '"}'
        req = urllib2.Request(
            "https://www.googleapis.com/urlshortener/v1/url",
            data=request_line,
            headers={"Content-Type" : "application/json"}
        )
        socket = urllib2.urlopen(req)
        response = socket.read()
        socket.close()
        jdict = json.loads(response)
        a = ShortUrl(longUrl=Url,shortUrl=jdict["id"])
        a.save()
        return a.shortUrl

def handlenotfound(request,suggestions = None):
    "Application's custom 404 handler."
    global common_data
    
    datas = {
        'tags' : Tag.objects.all(),
        'date_list' : \
        Post.objects.filter(yayinlandi=True).dates("pub_date","year")
    }
    
    if suggestions is not None:
        datas["suggestions"] = suggestions
    
    template = loader.get_template("blog_404.html")
    datas.update(common_data)
    icerik = Context(datas)
    return HttpResponseNotFound(template.render(icerik))
    
def handleServerError(request):
    "Application's custom server error handler."
    global common_data
    return render_to_response("blog_500.html",Context(comman_data))

@require_http_methods(["POST"])
def message(request):
    "Save's messages, and notifies admins via e-mail."
    
    # Spam verification.
    try:
        if int(time()) - request.session["last_message"] < 10:
            return HttpResponse("4")
    except:
        pass
    
    slug = request.POST["post"]
    message = request.POST["message"]
    
    try:
        p = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        p = None
    
    valid_message = False
    try:
        email = request.POST["email"]
    except:
        email = ""
    
    # E-mail verification.
    if email != "":
        if not re.match(
            "^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$",
            email
        ):
            return HttpResponse("5")
    # Message length verification
    if len(message) <= 500 and len(message) >= 5:
        valid_message = True
    
    # Send error codes.
    if p is None and valid_message is False:
        return HttpResponse("3")
    
    elif p is None:
        return HttpResponse("1")
    
    elif valid_message is False:
        return HttpResponse("2")
    
    # At this point, everything is ok.
    mes = Message.objects.create(
        post=p,
        message=request.POST['message'],
        email=email
    )
    mail_admins("Yeni mesaj", request.POST["message"])
    request.session["last_message"] = int(time())
    return HttpResponse("0")


@gzip_page
def homepage(request):
    "Shows 10 latest posts with their abstracts."
    global common_data
    query_set = Post.objects.filter(yayinlandi=True)
    latest = []
    for post in query_set.order_by("-pub_date")[:10]:
        latest.append((post,post.tags.all()))
    years = query_set.dates("pub_date","year")
    date_hierarchy = {}
    for year in years:
        date_hierarchy[year] = {}
        months = query_set.filter(pub_date__year=year.year).dates("pub_date","month")
        for month in months:
            date_hierarchy[year][month] = query_set.filter(pub_date__year=month.year,pub_date__month=month.month).count()
        
    datas = {
        'latest' : latest,
        'date_list' : query_set.dates("pub_date","year"),
        'date_hierarchy' : date_hierarchy,
        'etiket_listesi' : \
            # 10 tags with most most post count.
            # ordered by post count.
            Tag.objects.annotate(post_sayisi=Count('post')).\
            order_by("-post_sayisi")[:10],
    }
    datas.update(common_data)
    return render_to_response("blog_index.html",datas)

@gzip_page
@cache_page(3600)
def post_index(request):
    "Shows latest 30 post, without abstracts."
    global common_data
    datas = {
        'latest' : \
            Post.objects.filter(yayinlandi=True).order_by("-pub_date")[:30],
        'date_list' : \
            Post.objects.filter(yayinlandi=True).dates("pub_date","year"),
    }
    datas.update(common_data)
    return render_to_response("blog_post_index.html",datas)
    
@gzip_page
@cache_page(900)
def arsiv_index(request):
    global common_data
    datas = {
        'date_list' : \
            Post.objects.filter(yayinlandi=True).dates("pub_date","year")
    }
    datas.update(common_data)
    return render_to_response("blog_arsiv_index.html",datas)

@gzip_page
def post(request,slug):
    "Post details."
    global common_data
    try:
        p = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        
        # We will try to spelling correct the give url.
        suggestions = suggest(
            slug, 
            [p.slug for p in Post.objects.filter(yayinlandi=True)]
        )
       
        if len(suggestions) == 0:
            raise Http404
        elif len(suggestions) == 1:
            p = Post.objects.get(slug = suggestions[0])
            return HttpResponsePermanentRedirect(p.get_absolute_url())
        else:
            # if more than 1 suggestions, we will ask visitor to choose
            posts = [
                Post.objects.get(slug=suggestion) for 
                suggestion in suggestions
            ]
            
            suggestions = [p.get_absolute_url() for p in posts]
            
            return handlenotfound(request,suggestions)
        
    if p.yayinlandi or request.user.is_authenticated():
        datas = {
                'post': p,
                'tags' : p.tags.all(),
                'messages' : settings.BLOG_MESSAGES_ENABLED,
                }
        datas.update(common_data)
        
        relative_url = str(p.get_absolute_url())
        abs_url = "%s://%s%s" % (
            common_data["protocol"],
            common_data["domain"],
            relative_url
        )
        datas["shorturl"] = getShortUrl(abs_url) 

        return render_to_response(
            'blog_post.html', 
            datas, 
            context_instance=RequestContext(request)
        )
    else:
        raise Http404


@gzip_page
@cache_page(3600)
def tag(request,tag):
    "Lists all posts for a given tag, ordered by publication date."
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
            tags = [ 
                Tag.objects.get(slug=suggestion) for 
                suggestion in suggestions
            ]
            
            suggestions = [reverse("tag",args=[tag.slug]) for tag in tags]
            return handlenotfound(request,suggestions)
    post_set = tag.post_set.filter(yayinlandi=True).order_by("-pub_date")
    datas = {
            'tag' : tag,
            'latest_posts': post_set,
            }
    datas.update(common_data)
    return render_to_response('blog_tag.html', datas)


@gzip_page
@cache_page(3600)
def tag_index(request):
    "Lists all tags."
    datas = {'tags' : Tag.objects.all()}
    datas.update(common_data)
    return render_to_response('blog_tag_index.html', datas)
