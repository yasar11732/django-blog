# -*- coding:utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from blog.models import Post
from time import sleep

class suggestingboxtests(TestCase):
    
    """
    Hedefler:
    
    Eğer başarılı ise "0"
    Geçersiz url ise "1"
    geçersiz mesaj "2"
    ikisi birden ise "3"
    spam "4"
    
    
    """
    
    def setUp(self):
        self.p = Post.objects.create(title="deneme",slug="deneme",abstract="deneme",post="deneme",yayinlandi=True)
        self.p.save()
    
    def test_not_get(self):
        "get metoduna izin vermiyoruz"
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.get('/message',**kwargs)
        self.assertEqual(response.status_code,405)
    
    def test_successfull(self):
        "Başarılı bir mesaj ekle, 200 kodu dönmeli ve post objesine 1 adet mesaj eklenmeli"
        
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "deneme","message" : "pek iyi!"},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"0")
        self.assertEqual(self.p.message_set.all().count(),1)
        self.assertEqual(self.p.message_set.get(pk=1).message,"pek iyi!")
        
    def test_invalid_url(self):
        "Eğer url ile belirtilen post yoksa, response olarak 1 göndermeli"
        
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "asd","message" : "pek iyi!"},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"1")
        self.assertEqual(self.p.message_set.all().count(),0)
    def test_mail(self):
        "doğru mail adresinde 0 yanlış mail adresinde 5 almamız gerek"
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "deneme","message" : "pek iyi!","email":"yasar11732@gmail.com"},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"0")
        self.assertEqual(self.p.message_set.all().count(),1)
        
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "deneme","message" : "pek iyi!","email":"yasar11732gmail.com"},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"5")
        self.assertEqual(self.p.message_set.all().count(),1)
        
    def test_invalid_msg(self):
        "Eğer mesaj çok kısa(5 karakterden az) veya uzunsa(500 karakterden fazla) response olarak 2"
        
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "deneme","message" : "a"},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"2")
        self.assertEqual(self.p.message_set.all().count(),0)
        
        a = ""
        
        while len(a) < 510:
            a += "x"
            
        c = Client()
        response = c.post('/message',{"post" : "deneme","message" : a},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"2")
        self.assertEqual(self.p.message_set.all().count(),0)
        
    def test_invalid_url_and_message(self):
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "asdf","message" : "a"},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"3")
        self.assertEqual(self.p.message_set.all().count(),0)
        
        a = ""
        
        while len(a) < 510:
            a += "x"
            
        
        c = Client()
        
        response = c.post('/message',{"post" : "asdf","message" : a},**kwargs)
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"3")
        self.assertEqual(self.p.message_set.all().count(),0)
        
    def test_spam(self):
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        c.post('/message',{"post" : "deneme","message" : "pek iyi!"},**kwargs)
        for a in range(0,20):
            response = c.post('/message',{"post" : "deneme","message" : "pek iyi!"},**kwargs)
            self.assertEqual(str(response.content),"4")
        
        self.assertEqual(self.p.message_set.all().count(),1)
        
    def test_not_spam(self):
        "kullanıcı 10 saniyenin ardından yeni mesaj gönderebilmeli"
        c = Client()
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = c.post('/message',{"post" : "deneme","message" : "pek iyi!"},**kwargs)
        self.assertEqual(str(response.content),"0")
        self.assertEqual(self.p.message_set.all().count(),1)
        
        sleep(11)
        
        response = c.post('/message',{"post" : "deneme","message" : "pek iyi!"},**kwargs)
        self.assertEqual(str(response.content),"0")
        self.assertEqual(self.p.message_set.all().count(),2)
     