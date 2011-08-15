# -*- coding:utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from blog.models import Post

class suggestingboxtests(TestCase):
    
    """
    Hedefler:
    
    Eğer başarılı ise "0"
    Geçersiz url ise "1"
    geçersiz mesaj "2"
    ikisi birden ise "3"
    spam "4"
    
    Geçersiz url için, o slug alanına ait bir makale var mı?
    """
    
    def setUp(self):
        self.p = Post.objects.create(title="deneme",slug="deneme",abstract="deneme",post="deneme",yayinlandi=True)
        self.p.save()
        
    def test_not_get(self):
        "get metoduna izin vermiyoruz"
        c = Client()
        response = c.get('/message')
        self.assertEqual(response.status_code,405)
    
    def test_successfull(self):
        "Başarılı bir mesaj ekle, 200 kodu dönmeli ve post objesine 1 adet mesaj eklenmeli"
        
        c = Client()
        
        response = c.post('/message',{"post" : "deneme","message" : "pek iyi!"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"0")
        self.assertEqual(self.p.message_set.all().count(),1)
        self.assertEqual(self.p.message_set.get(pk=1).message,"pek iyi!")
        
    def test_invalid_url(self):
        "Eğer url ile belirtilen post yoksa, response olarak 1 göndermeli"
        
        c = Client()
        
        response = c.post('/message',{"post" : "asd","message" : "pek iyi!"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"1")
        self.assertEqual(self.p.message_set.all().count(),0)
        
    def test_invalid_msg(self):
        "Eğer mesaj çok kısa(5 karakterden az) veya uzunsa(500 karakterden fazla) response olarak 2"
        
        c = Client()
        
        response = c.post('/message',{"post" : "deneme","message" : "a"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"2")
        self.assertEqual(self.p.message_set.all().count(),0)
        
        a = ""
        
        while len(a) < 510:
            a += "x"
            
        c = Client()
        response = c.post('/message',{"post" : "deneme","message" : a})
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"2")
        self.assertEqual(self.p.message_set.all().count(),0)
        
    def test_invalid_url_and_message(self):
        c = Client()
        
        response = c.post('/message',{"post" : "asdf","message" : "a"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"3")
        self.assertEqual(self.p.message_set.all().count(),0)
        
        a = ""
        
        while len(a) < 510:
            a += "x"
            
        
        c = Client()
        
        response = c.post('/message',{"post" : "asdf","message" : a})
        self.assertEqual(response.status_code,200)
        self.assertEqual(str(response.content),"3")
        self.assertEqual(self.p.message_set.all().count(),0)
        
    def test_spam(self):
        c = Client()
        c.post('/message',{"post" : "deneme","message" : "pek iyi!"})
        for a in range(0,20):
            response = c.post('/message',{"post" : "deneme","message" : "pek iyi!"})
            self.assertEqual(str(response.content),"4")
        
        self.assertEqual(self.p.message_set.all().count(),1)
        
     