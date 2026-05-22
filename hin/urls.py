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
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # User Management (Superuser only)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Contact enquiries
    path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('enquiries/<int:pk>/', views.enquiry_detail, name='enquiry_detail'),
    path('enquiries/<int:pk>/toggle-read/', views.enquiry_toggle_read, name='enquiry_toggle_read'),
    path('enquiries/<int:pk>/delete/', views.enquiry_delete, name='enquiry_delete'),
    
    # Services
    
    path('services/', views.public_services, name='public_services'),
    path('servicelist/', views.service_list, name='service_list'),
    path('services/manage/', views.service_manage, name='service_manage'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    
    # Blogs
    path('blogs/', views.public_blogs, name='public_blogs'),
    path('bloglist/', views.blog_list, name='blog_list'),
    path('blogs/manage/', views.blog_manage, name='blog_manage'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blogs/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    

    path('clients/', views.public_clients, name='public_clients'),
    path('clientlist/', views.client_list, name='client_list'),
    path('clients/manage/', views.client_manage, name='client_manage'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)