# hin/forms.py - Updated permission mappings

from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ContactEnquiry, Service, Blog, Client

# ==================== AUTHENTICATION FORMS ====================



class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# ==================== USER MANAGEMENT FORMS WITH PERMISSIONS ====================

class UserCreateWithPermissionsForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_staff = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    # Permission fields grouped by module - USING CORRECT PERMISSION NAMES
    # Contact Enquiry Permissions (Django default names)
    can_view_contactenquiry = forms.BooleanField(required=False, label='View Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_contactenquiry = forms.BooleanField(required=False, label='Add Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_contactenquiry = forms.BooleanField(required=False, label='Change Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_contactenquiry = forms.BooleanField(required=False, label='Delete Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    # Service Permissions (Django default names)
    can_view_service = forms.BooleanField(required=False, label='View Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_service = forms.BooleanField(required=False, label='Add Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_service = forms.BooleanField(required=False, label='Change Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_service = forms.BooleanField(required=False, label='Delete Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    # Blog Permissions (Django default names)
    can_view_blog = forms.BooleanField(required=False, label='View Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_blog = forms.BooleanField(required=False, label='Add Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_blog = forms.BooleanField(required=False, label='Change Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_blog = forms.BooleanField(required=False, label='Delete Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    # Client Permissions (Django default names)
    can_view_client = forms.BooleanField(required=False, label='View Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_client = forms.BooleanField(required=False, label='Add Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_client = forms.BooleanField(required=False, label='Change Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_client = forms.BooleanField(required=False, label='Delete Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # Clear existing permissions
            user.user_permissions.clear()
            
            # List of permission fields to check
            permission_fields = [
                'can_view_contactenquiry', 'can_add_contactenquiry', 'can_change_contactenquiry', 'can_delete_contactenquiry',
                'can_view_service', 'can_add_service', 'can_change_service', 'can_delete_service',
                'can_view_blog', 'can_add_blog', 'can_change_blog', 'can_delete_blog',
                'can_view_client', 'can_add_client', 'can_change_client', 'can_delete_client',
            ]
            
            # Assign selected permissions
            for field_name in permission_fields:
                if self.cleaned_data.get(field_name):
                    # Extract permission codename (remove 'can_' prefix)
                    perm_codename = field_name[4:]  # Remove 'can_' from the beginning
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        user.user_permissions.add(permission)
                    except Permission.DoesNotExist:
                        pass
        
        return user

class UserEditWithPermissionsForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_staff = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    # Permission fields - USING CORRECT DJANGO DEFAULT NAMES
    can_view_contactenquiry = forms.BooleanField(required=False, label='View Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_contactenquiry = forms.BooleanField(required=False, label='Add Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_contactenquiry = forms.BooleanField(required=False, label='Change Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_contactenquiry = forms.BooleanField(required=False, label='Delete Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    can_view_service = forms.BooleanField(required=False, label='View Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_service = forms.BooleanField(required=False, label='Add Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_service = forms.BooleanField(required=False, label='Change Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_service = forms.BooleanField(required=False, label='Delete Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    can_view_blog = forms.BooleanField(required=False, label='View Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_blog = forms.BooleanField(required=False, label='Add Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_blog = forms.BooleanField(required=False, label='Change Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_blog = forms.BooleanField(required=False, label='Delete Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    can_view_client = forms.BooleanField(required=False, label='View Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_add_client = forms.BooleanField(required=False, label='Add Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_change_client = forms.BooleanField(required=False, label='Change Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    can_delete_client = forms.BooleanField(required=False, label='Delete Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        
        # Load current user permissions if editing existing user
        if self.instance and self.instance.pk:
            current_perms = self.instance.user_permissions.values_list('codename', flat=True)
            
            # Set initial values for permission checkboxes
            permission_fields = [
                'view_contactenquiry', 'add_contactenquiry', 'change_contactenquiry', 'delete_contactenquiry',
                'view_service', 'add_service', 'change_service', 'delete_service',
                'view_blog', 'add_blog', 'change_blog', 'delete_blog',
                'view_client', 'add_client', 'change_client', 'delete_client',
            ]
            
            for perm_codename in permission_fields:
                field_name = f'can_{perm_codename}'
                if field_name in self.fields:
                    self.fields[field_name].initial = perm_codename in current_perms
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # Clear existing permissions
            user.user_permissions.clear()
            
            # List of permission fields to check
            permission_fields = [
                'can_view_contactenquiry', 'can_add_contactenquiry', 'can_change_contactenquiry', 'can_delete_contactenquiry',
                'can_view_service', 'can_add_service', 'can_change_service', 'can_delete_service',
                'can_view_blog', 'can_add_blog', 'can_change_blog', 'can_delete_blog',
                'can_view_client', 'can_add_client', 'can_change_client', 'can_delete_client',
            ]
            
            # Assign selected permissions
            for field_name in permission_fields:
                if self.cleaned_data.get(field_name):
                    perm_codename = field_name[4:]  # Remove 'can_' prefix
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        user.user_permissions.add(permission)
                    except Permission.DoesNotExist:
                        pass
        
        return user

# ==================== CMS FORMS (keep as is) ====================

class ContactEnquiryForm(forms.ModelForm):
    class Meta:
        model = ContactEnquiry
        fields = ['first_name', 'last_name', 'experience_level', 'email', 'mobile_no']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9876543210'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'short_description', 'full_description', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Title'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description (max 500 chars)'}),
            'full_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Detailed description'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'featured_image', 'short_description', 'content', 'author', 'category', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Blog Title'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief summary (max 500 chars)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 12, 'placeholder': 'Full blog content'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category (e.g., DevOps, Docker, CI/CD)'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['company_name', 'company_type', 'logo', 'website_url', 'is_active']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'company_type': forms.Select(attrs={'class': 'form-select'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://company.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }