from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'hin'

urlpatterns = [
    # Static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    
    # Contact enquiries
    path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('enquiries/<int:pk>/', views.enquiry_detail, name='enquiry_detail'),
    path('enquiries/<int:pk>/toggle-read/', views.enquiry_toggle_read, name='enquiry_toggle_read'),
    path('enquiries/<int:pk>/delete/', views.enquiry_delete, name='enquiry_delete'),
    
    # Services
    path('services/', views.service_list, name='service_list'),
    path('services/manage/', views.service_manage, name='service_manage'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    
    # Blogs
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/manage/', views.blog_manage, name='blog_manage'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blogs/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    
    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/manage/', views.client_manage, name='client_manage'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
