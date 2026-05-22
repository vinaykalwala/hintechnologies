from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User

class ContactEnquiry(models.Model):
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('experienced', 'Experienced'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    email = models.EmailField()
    mobile_no = models.CharField(max_length=15)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    def get_absolute_url(self):
        return reverse('enquiry_detail', kwargs={'pk': self.pk})

class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    short_description = models.TextField(max_length=500)
    full_description = models.TextField()
    image = models.ImageField(upload_to='service_images/', blank=True, null=True, help_text="Upload service image")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('hin:public_services')

class Blog(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True, max_length=300)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    short_description = models.TextField(max_length=500)
    content = models.TextField()
    author = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

class Client(models.Model):
    COMPANY_TYPES = [
        ('hiring_partner', 'Hiring Partner'),
        ('corporate_client', 'Corporate Client'),
    ]
    
    company_name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    logo = models.ImageField(upload_to='client_logos/')
    website_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company_name']
        
    
    def __str__(self):
        return self.company_name
    
    def get_absolute_url(self):
        return reverse('client_list')

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"