from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ContactEnquiry, Service, Blog, Client

# ==================== AUTHENTICATION FORMS ====================

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

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
    
    # Permission fields grouped by module
    # Contact Enquiry Permissions
    can_view_enquiries = forms.BooleanField(required=False, label='View Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_enquiries = forms.BooleanField(required=False, label='Change Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_enquiries = forms.BooleanField(required=False, label='Delete Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
    # Service Permissions
    can_add_services = forms.BooleanField(required=False, label='Add Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_services = forms.BooleanField(required=False, label='Change Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_services = forms.BooleanField(required=False, label='Delete Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_view_services = forms.BooleanField(required=False, label='View Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
    # Blog Permissions
    can_add_blogs = forms.BooleanField(required=False, label='Add Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_blogs = forms.BooleanField(required=False, label='Change Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_blogs = forms.BooleanField(required=False, label='Delete Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_view_blogs = forms.BooleanField(required=False, label='View Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
    # Client Permissions
    can_add_clients = forms.BooleanField(required=False, label='Add Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_clients = forms.BooleanField(required=False, label='Change Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_clients = forms.BooleanField(required=False, label='Delete Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_view_clients = forms.BooleanField(required=False, label='View Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
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
            
            # Dictionary mapping form field to permission codename
            permission_mapping = {
                'can_view_enquiries': 'view_contactenquiry',
                'can_change_enquiries': 'change_contactenquiry',
                'can_delete_enquiries': 'delete_contactenquiry',
                'can_add_services': 'add_service',
                'can_change_services': 'change_service',
                'can_delete_services': 'delete_service',
                'can_view_services': 'view_service',
                'can_add_blogs': 'add_blog',
                'can_change_blogs': 'change_blog',
                'can_delete_blogs': 'delete_blog',
                'can_view_blogs': 'view_blog',
                'can_add_clients': 'add_client',
                'can_change_clients': 'change_client',
                'can_delete_clients': 'delete_client',
                'can_view_clients': 'view_client',
            }
            
            # Assign selected permissions
            for field_name, perm_codename in permission_mapping.items():
                if self.cleaned_data.get(field_name):
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
    
    # Permission fields grouped by module
    can_view_enquiries = forms.BooleanField(required=False, label='View Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_enquiries = forms.BooleanField(required=False, label='Change Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_enquiries = forms.BooleanField(required=False, label='Delete Contact Enquiries', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
    can_add_services = forms.BooleanField(required=False, label='Add Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_services = forms.BooleanField(required=False, label='Change Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_services = forms.BooleanField(required=False, label='Delete Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_view_services = forms.BooleanField(required=False, label='View Services', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
    can_add_blogs = forms.BooleanField(required=False, label='Add Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_blogs = forms.BooleanField(required=False, label='Change Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_blogs = forms.BooleanField(required=False, label='Delete Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_view_blogs = forms.BooleanField(required=False, label='View Blogs', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
    can_add_clients = forms.BooleanField(required=False, label='Add Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_change_clients = forms.BooleanField(required=False, label='Change Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_delete_clients = forms.BooleanField(required=False, label='Delete Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    can_view_clients = forms.BooleanField(required=False, label='View Clients', widget=forms.CheckboxInput(attrs={'class': 'form-check-input permission-check'}))
    
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
            self.fields['can_view_enquiries'].initial = 'view_contactenquiry' in current_perms
            self.fields['can_change_enquiries'].initial = 'change_contactenquiry' in current_perms
            self.fields['can_delete_enquiries'].initial = 'delete_contactenquiry' in current_perms
            
            self.fields['can_add_services'].initial = 'add_service' in current_perms
            self.fields['can_change_services'].initial = 'change_service' in current_perms
            self.fields['can_delete_services'].initial = 'delete_service' in current_perms
            self.fields['can_view_services'].initial = 'view_service' in current_perms
            
            self.fields['can_add_blogs'].initial = 'add_blog' in current_perms
            self.fields['can_change_blogs'].initial = 'change_blog' in current_perms
            self.fields['can_delete_blogs'].initial = 'delete_blog' in current_perms
            self.fields['can_view_blogs'].initial = 'view_blog' in current_perms
            
            self.fields['can_add_clients'].initial = 'add_client' in current_perms
            self.fields['can_change_clients'].initial = 'change_client' in current_perms
            self.fields['can_delete_clients'].initial = 'delete_client' in current_perms
            self.fields['can_view_clients'].initial = 'view_client' in current_perms
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            # Clear existing permissions
            user.user_permissions.clear()
            
            # Dictionary mapping form field to permission codename
            permission_mapping = {
                'can_view_enquiries': 'view_contactenquiry',
                'can_change_enquiries': 'change_contactenquiry',
                'can_delete_enquiries': 'delete_contactenquiry',
                'can_add_services': 'add_service',
                'can_change_services': 'change_service',
                'can_delete_services': 'delete_service',
                'can_view_services': 'view_service',
                'can_add_blogs': 'add_blog',
                'can_change_blogs': 'change_blog',
                'can_delete_blogs': 'delete_blog',
                'can_view_blogs': 'view_blog',
                'can_add_clients': 'add_client',
                'can_change_clients': 'change_client',
                'can_delete_clients': 'delete_client',
                'can_view_clients': 'view_client',
            }
            
            # Assign selected permissions
            for field_name, perm_codename in permission_mapping.items():
                if self.cleaned_data.get(field_name):
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        user.user_permissions.add(permission)
                    except Permission.DoesNotExist:
                        pass
        
        return user

# ==================== EXISTING FORMS (keep from previous) ====================

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
        fields = ['title', 'short_description', 'full_description', 'icon', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Title'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description (max 500 chars)'}),
            'full_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Detailed description'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-docker, fa-kubernetes, etc.'}),
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