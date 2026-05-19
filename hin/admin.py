from django.contrib import admin
from .models import ContactEnquiry, Service, Blog, Client

@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'mobile_no', 'experience_level', 'is_read', 'created_at']
    list_filter = ['experience_level', 'is_read', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'mobile_no']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'author', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_type', 'is_active', 'created_at']
    list_filter = ['company_type', 'is_active', 'created_at']
    search_fields = ['company_name']
    readonly_fields = ['created_at', 'updated_at']