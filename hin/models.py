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
        permissions = [
            ('view_contactenquiry', 'Can view contact enquiry'),
            ('change_contactenquiry', 'Can change contact enquiry'),
            ('delete_contactenquiry', 'Can delete contact enquiry'),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    def get_absolute_url(self):
        return reverse('enquiry_detail', kwargs={'pk': self.pk})

class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    short_description = models.TextField(max_length=500)
    full_description = models.TextField()
    icon = models.CharField(max_length=100, help_text="FontAwesome icon class, e.g., 'fa-docker'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        permissions = [
            ('add_service', 'Can add service'),
            ('change_service', 'Can change service'),
            ('delete_service', 'Can delete service'),
            ('view_service', 'Can view service'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('service_list')

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
        permissions = [
            ('add_blog', 'Can add blog'),
            ('change_blog', 'Can change blog'),
            ('delete_blog', 'Can delete blog'),
            ('view_blog', 'Can view blog'),
        ]
    
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
        permissions = [
            ('add_client', 'Can add client'),
            ('change_client', 'Can change client'),
            ('delete_client', 'Can delete client'),
            ('view_client', 'Can view client'),
        ]
    
    def __str__(self):
        return self.company_name
    
    def get_absolute_url(self):
        return reverse('client_list')