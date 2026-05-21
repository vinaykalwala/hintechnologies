from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ContactEnquiry, Service, Blog, Client
from .forms import ContactEnquiryForm, ServiceForm, BlogForm, ClientForm

# ==================== STATIC PAGES ====================

def home(request):
    services = Service.objects.filter(is_active=True)[:6]
    blogs = Blog.objects.filter(is_published=True)[:3]
    hiring_partners = Client.objects.filter(company_type='hiring_partner', is_active=True)[:12]
    context = {
        'services': services,
        'blogs': blogs,
        'hiring_partners': hiring_partners,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')



# ==================== CONTACT ENQUIRY ====================

def contact(request):
    if request.method == 'POST':
        form = ContactEnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your enquiry has been submitted. We will contact you within 24 hours.')
            return redirect('hin:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactEnquiryForm()
    
    return render(request, 'contact.html', {'form': form})

@login_required
@permission_required('hin.view_contactenquiry', raise_exception=True)
def enquiry_list(request):
    enquiries = ContactEnquiry.objects.all()
    
    # Filter by read status
    read_filter = request.GET.get('read')
    if read_filter == 'unread':
        enquiries = enquiries.filter(is_read=False)
    elif read_filter == 'read':
        enquiries = enquiries.filter(is_read=True)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        enquiries = enquiries.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mobile_no__icontains=search_query)
        )
    
    paginator = Paginator(enquiries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'contact/enquiry_list.html', {
        'enquiries': page_obj,
        'read_filter': read_filter,
        'search_query': search_query,
    })

@login_required
@permission_required('hin.view_contactenquiry', raise_exception=True)
def enquiry_detail(request, pk):
    enquiry = get_object_or_404(ContactEnquiry, pk=pk)
    if not enquiry.is_read:
        enquiry.is_read = True
        enquiry.save()
    return render(request, 'contact/enquiry_detail.html', {'enquiry': enquiry})

@login_required
@permission_required('hin.change_contactenquiry', raise_exception=True)
def enquiry_toggle_read(request, pk):
    enquiry = get_object_or_404(ContactEnquiry, pk=pk)
    enquiry.is_read = not enquiry.is_read
    enquiry.save()
    messages.success(request, f'Enquiry marked as {"read" if enquiry.is_read else "unread"}')
    return redirect('hin:enquiry_detail', pk=enquiry.pk)

from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@login_required
@permission_required('hin.delete_contactenquiry', raise_exception=True)
@require_http_methods(["POST"])
def enquiry_delete(request, pk):
    """
    Delete an enquiry via AJAX POST request.
    Returns JSON response with success/error message.
    """
    try:
        enquiry = get_object_or_404(ContactEnquiry, pk=pk)
        enquiry_name = f"{enquiry.first_name} {enquiry.last_name}"
        enquiry.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Enquiry from {enquiry_name} deleted successfully.',
            'enquiry_id': pk
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting enquiry: {str(e)}'
        }, status=400)
# ==================== SERVICES ====================

def public_services(request):
    """Public facing services page - no admin controls"""
    services = Service.objects.filter(is_active=True)
    
    # Search functionality for public
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(services, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'search_query': search_query,
        'total_services': services.count(),
    }
    return render(request, 'services/public_services.html', context)

# ==================== ADMIN SERVICES LIST VIEW ====================

def service_list(request):
    """Admin view for listing services (read-only for public with login)"""
    services = Service.objects.all()
    
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'services/service_list.html', {
        'services': page_obj,
        'search_query': search_query,
    })

# ==================== ADMIN SERVICE MANAGEMENT VIEW ====================

@login_required
@permission_required('hin.add_service', raise_exception=True)
def service_manage(request):
    """Admin view for adding/editing services"""
    edit_id = request.GET.get('edit')
    service_to_edit = None
    
    if edit_id:
        service_to_edit = get_object_or_404(Service, pk=edit_id)
        if not request.user.has_perm('hin.change_service'):
            messages.error(request, 'You don\'t have permission to edit services.')
            return redirect('hin:service_list')
    
    if request.method == 'POST':
        if service_to_edit:
            form = ServiceForm(request.POST, request.FILES, instance=service_to_edit)
        else:
            form = ServiceForm(request.POST, request.FILES)
        
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.title}" saved successfully.')
            return redirect('hin:service_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm(instance=service_to_edit) if service_to_edit else ServiceForm()
    
    all_services = Service.objects.all()
    can_delete = request.user.has_perm('hin.delete_service')
    
    return render(request, 'services/service_list.html', {
        'form': form,
        'services': all_services,
        'editing_service': service_to_edit,
        'can_delete': can_delete,
    })

# ==================== ADMIN SERVICE DELETE VIEW ====================

@login_required
@permission_required('hin.delete_service', raise_exception=True)
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service_title = service.title
        service.delete()
        messages.success(request, f'Service "{service_title}" deleted successfully.')
        return redirect('hin:service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})
# ==================== BLOGS ====================

def blog_list(request):
    blogs = Blog.objects.filter(is_published=True)
    
    # Category filter
    category = request.GET.get('category')
    if category:
        blogs = blogs.filter(category__iexact=category)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    paginator = Paginator(blogs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter
    categories = Blog.objects.filter(is_published=True).values_list('category', flat=True).distinct()
    
    return render(request, 'blogs/blog_list.html', {
        'blogs': page_obj,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    recent_blogs = Blog.objects.filter(is_published=True).exclude(id=blog.id)[:3]
    return render(request, 'blogs/blog_detail.html', {
        'blog': blog,
        'recent_blogs': recent_blogs,
    })

@login_required
@permission_required('hin.add_blog', raise_exception=True)
@permission_required('hin.change_blog', raise_exception=True)
def blog_manage(request):
    edit_id = request.GET.get('edit')
    blog_to_edit = None
    
    if edit_id:
        blog_to_edit = get_object_or_404(Blog, pk=edit_id)
        if not request.user.has_perm('hin.change_blog'):
            messages.error(request, 'You don\'t have permission to edit blogs.')
            return redirect('hin:blog_list')
    
    if request.method == 'POST':
        if blog_to_edit:
            form = BlogForm(request.POST, request.FILES, instance=blog_to_edit)
        else:
            form = BlogForm(request.POST, request.FILES)
        
        if form.is_valid():
            blog = form.save()
            messages.success(request, f'Blog "{blog.title}" saved successfully.')
            return redirect('hin:blog_detail', slug=blog.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogForm(instance=blog_to_edit) if blog_to_edit else BlogForm()
    
    all_blogs = Blog.objects.all()
    can_delete = request.user.has_perm('hin.delete_blog')
    
    return render(request, 'blogs/blog_list.html', {
        'form': form,
        'blogs': all_blogs,
        'editing_blog': blog_to_edit,
        'can_delete': can_delete,
        'is_management': True,
    })

@login_required
@permission_required('hin.delete_blog', raise_exception=True)
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog_title = blog.title
        blog.delete()
        messages.success(request, f'Blog "{blog_title}" deleted successfully.')
        return redirect('blog_list')
    return render(request, 'blogs/blog_confirm_delete.html', {'blog': blog})

# ==================== CLIENTS ====================

def client_list(request):
    hiring_partners = Client.objects.filter(company_type='hiring_partner', is_active=True)
    corporate_clients = Client.objects.filter(company_type='corporate_client', is_active=True)
    
    return render(request, 'clients/client_list.html', {
        'hiring_partners': hiring_partners,
        'corporate_clients': corporate_clients,
    })

@login_required
@permission_required('hin.add_client', raise_exception=True)
@permission_required('hin.change_client', raise_exception=True)
def client_manage(request):
    edit_id = request.GET.get('edit')
    client_to_edit = None
    
    if edit_id:
        client_to_edit = get_object_or_404(Client, pk=edit_id)
        if not request.user.has_perm('hin.change_client'):
            messages.error(request, 'You don\'t have permission to edit clients.')
            return redirect('hin:client_list')
    
    if request.method == 'POST':
        if client_to_edit:
            form = ClientForm(request.POST, request.FILES, instance=client_to_edit)
        else:
            form = ClientForm(request.POST, request.FILES)
        
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client "{client.company_name}" saved successfully.')
            return redirect('hin:client_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client_to_edit) if client_to_edit else ClientForm()
    
    hiring_partners = Client.objects.filter(company_type='hiring_partner')
    corporate_clients = Client.objects.filter(company_type='corporate_client')
    can_delete = request.user.has_perm('hin.delete_client')
    
    return render(request, 'clients/client_list.html', {
        'form': form,
        'hiring_partners': hiring_partners,
        'corporate_clients': corporate_clients,
        'editing_client': client_to_edit,
        'can_delete': can_delete,
        'is_management': True,
    })

@login_required
@permission_required('hin.delete_client', raise_exception=True)
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client_name = client.company_name
        client.delete()
        messages.success(request, f'Client "{client_name}" deleted successfully.')
        return redirect('hin:client_list')
    return render(request, 'clients/client_confirm_delete.html', {'client': client})

# Add these imports and views to your existing views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User, Permission
from .models import ContactEnquiry, Service, Blog, Client
from .forms import (
    ContactEnquiryForm, ServiceForm, BlogForm, ClientForm,
    LoginForm, UserProfileForm,
    UserCreateWithPermissionsForm, UserEditWithPermissionsForm
)

# ==================== HELPER FUNCTIONS ====================

def is_superuser(user):
    return user.is_superuser

def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

# ==================== AUTHENTICATION VIEWS ====================

def user_login(request):
    if request.user.is_authenticated:
        return redirect('hin:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login, authenticate
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('hin:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('hin:home')

@login_required
def dashboard(request):
    total_enquiries = ContactEnquiry.objects.count()
    unread_enquiries = ContactEnquiry.objects.filter(is_read=False).count()
    total_services = Service.objects.count()
    active_services = Service.objects.filter(is_active=True).count()
    total_blogs = Blog.objects.count()
    published_blogs = Blog.objects.filter(is_published=True).count()
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    recent_enquiries = ContactEnquiry.objects.order_by('-created_at')[:2]

    
    context = {
        'total_enquiries': total_enquiries,
        'unread_enquiries': unread_enquiries,
        'total_services': total_services,
        'active_services': active_services,
        'total_blogs': total_blogs,
        'published_blogs': published_blogs,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'total_users': total_users,
        'recent_enquiries': recent_enquiries,
    }
    return render(request, 'auth/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('hin:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'auth/profile.html', {'form': form})

# ==================== USER MANAGEMENT VIEWS WITH PERMISSIONS (SUPERUSER ONLY) ====================

@login_required
@user_passes_test(is_superuser)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    role_filter = request.GET.get('role')
    if role_filter == 'superuser':
        users = users.filter(is_superuser=True)
    elif role_filter == 'staff':
        users = users.filter(is_staff=True, is_superuser=False)
    elif role_filter == 'active':
        users = users.filter(is_active=True)
    elif role_filter == 'inactive':
        users = users.filter(is_active=False)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/user_list.html', {
        'users': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
    })

@login_required
@user_passes_test(is_superuser)
def user_create(request):
    if request.method == 'POST':
        form = UserCreateWithPermissionsForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been created successfully with selected permissions!')
            return redirect('hin:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreateWithPermissionsForm()
    
    return render(request, 'users/user_create.html', {'form': form})

@login_required
@user_passes_test(is_superuser)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.warning(request, 'Please use the Profile page to edit your own account.')
        return redirect('hin:profile')
    
    if request.method == 'POST':
        form = UserEditWithPermissionsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" has been updated successfully with new permissions!')
            return redirect('hin:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserEditWithPermissionsForm(instance=user)
    
    return render(request, 'users/user_edit.html', {'form': form, 'edit_user': user})

@login_required
@user_passes_test(is_superuser)
def user_delete(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(
            request,
            'You cannot delete your own account.'
        )
        return redirect('hin:user_list')

    username = user.username
    user.delete()

    messages.success(
        request,
        f'User "{username}" deleted successfully!'
    )

    return redirect('hin:user_list')

def public_clients(request):
    """Public facing clients page - no admin controls"""
    hiring_partners = Client.objects.filter(company_type='hiring_partner', is_active=True)
    corporate_clients = Client.objects.filter(company_type='corporate_client', is_active=True)
    
    context = {
        'hiring_partners': hiring_partners,
        'corporate_clients': corporate_clients,
    }
    return render(request, 'clients/public_clients.html', context)

def public_blogs(request):
    """Public facing blogs page - no admin controls, no detail page"""
    blogs = Blog.objects.filter(is_published=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category')
    if category:
        blogs = blogs.filter(category__iexact=category)
    
    # Get all categories for filter dropdown
    categories = Blog.objects.filter(is_published=True).values_list('category', flat=True).distinct()
    
    # Pagination (9 blogs per page)
    paginator = Paginator(blogs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blogs': page_obj,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
        'total_blogs': blogs.count(),
    }
    return render(request, 'blogs/public_blogs.html', context)
