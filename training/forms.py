from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    StudentProfile, Batch, StudentBatch, DailySession,
    Project, StudentProjectSubmission, Deliverable
)

class StudentSignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    qualification = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Qualification'}))
    experience = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Previous experience if any'}), required=False)
    
    class Meta:
        model = StudentProfile
        fields = ['phone', 'qualification', 'experience']
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already registered.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create the User first
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        
        # Use get_or_create to avoid IntegrityError from signal
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': self.cleaned_data['phone'],
                'qualification': self.cleaned_data['qualification'],
                'experience': self.cleaned_data['experience'],
                'status': 'active'
            }
        )
        
        # If profile already existed, update it
        if not created:
            student_profile.phone = self.cleaned_data['phone']
            student_profile.qualification = self.cleaned_data['qualification']
            student_profile.experience = self.cleaned_data['experience']
            student_profile.status = 'active'
            if commit:
                student_profile.save()
        
        return student_profile

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'description', 'start_date', 'end_date', 'total_days', 'batch_capacity', 'number_of_projects', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'batch_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_projects': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class StudentBatchForm(forms.ModelForm):
    class Meta:
        model = StudentBatch
        fields = ['student', 'batch', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'batch': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = StudentProfile.objects.filter(status='active')
        self.fields['batch'].queryset = Batch.objects.exclude(status='completed').exclude(status='cancelled')

class DailySessionForm(forms.ModelForm):
    class Meta:
        model = DailySession
        fields = ['batch', 'day_number', 'title', 'topic', 'session_date', 'notes', 'recording_link']
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-select', 'id': 'id_batch'}),
            'day_number': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_day_number'}),  # Removed readonly
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'session_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recording_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make day_number optional
        self.fields['day_number'].required = False
        self.fields['day_number'].label = "Day Number (Auto-generated)"
        self.fields['day_number'].help_text = "This will be automatically calculated based on existing sessions"

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'batch', 'assigned_student', 'due_date', 'project_number', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'batch': forms.Select(attrs={'class': 'form-select', 'id': 'id_batch'}),
            'assigned_student': forms.Select(attrs={'class': 'form-select', 'id': 'id_assigned_student'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'project_number': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_project_number'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_student'].queryset = StudentProfile.objects.filter(status='active')
        self.fields['assigned_student'].required = False
        self.fields['batch'].required = False
        
        # For edit mode, we'll handle readonly in the template, not with disabled attribute
        if self.instance and self.instance.pk:
            # Editing existing project - make project_number not editable but still submit
            self.fields['project_number'].widget.attrs['readonly'] = True
            self.fields['project_number'].help_text = "Project number cannot be changed after creation"
        else:
            # New project
            self.fields['project_number'].required = False
            self.fields['project_number'].help_text = "Leave empty for auto-increment"
    
    def clean(self):
        cleaned_data = super().clean()
        batch = cleaned_data.get('batch')
        assigned_student = cleaned_data.get('assigned_student')
        project_number = cleaned_data.get('project_number')
        
        if not batch and not assigned_student:
            raise ValidationError('Either batch or assigned student must be selected.')
        
        if batch and assigned_student:
            raise ValidationError('Cannot assign to both batch and individual student.')
        
        # Only validate max projects for NEW projects
        if batch and not self.instance.pk:
            active_projects_count = Project.objects.filter(
                batch=batch
            ).exclude(status='completed').count()
            
            if active_projects_count >= batch.number_of_projects:
                raise ValidationError(
                    f'Cannot add more projects. This batch already has {batch.number_of_projects} '
                    f'active/pending projects. Complete or archive existing projects first.'
                )
        
        # Validate project number uniqueness (skip for auto-generated and edits)
        if batch and project_number and not self.instance.pk:
            if Project.objects.filter(batch=batch, project_number=project_number).exists():
                raise ValidationError(f'Project number {project_number} already exists for this batch.')
        
        return cleaned_data

class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = StudentProjectSubmission
        fields = ['github_link', 'live_link', 'zip_file', 'remarks']
        widgets = {
            'github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username/repo'}),
            'live_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://your-project-url.com'}),
            'zip_file': forms.FileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional remarks...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make at least one field required
        self.fields['github_link'].required = False
        self.fields['live_link'].required = False
        self.fields['zip_file'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        github_link = cleaned_data.get('github_link')
        live_link = cleaned_data.get('live_link')
        zip_file = cleaned_data.get('zip_file')
        remarks = cleaned_data.get('remarks')
        
        # Check if at least one submission method is provided
        if not github_link and not live_link and not zip_file:
            raise ValidationError(
                'Please provide at least one of the following: GitHub link, Live Demo link, or Project files.'
            )
        
        # Validate GitHub URL format
        if github_link and 'github.com' not in github_link:
            raise ValidationError('Please provide a valid GitHub repository URL.')
        
        # Validate file size (max 50MB)
        if zip_file:
            if zip_file.size > 50 * 1024 * 1024:  # 50MB in bytes
                raise ValidationError('File size cannot exceed 50MB.')
        
        return cleaned_data

class ReviewSubmissionForm(forms.ModelForm):
    class Meta:
        model = StudentProjectSubmission
        fields = ['status', 'admin_feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Feedback for student...'}),
        }

class DeliverableForm(forms.ModelForm):
    class Meta:
        model = Deliverable
        fields = ['title', 'description', 'deliverable_type', 'batch', 'assigned_student', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'deliverable_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_deliverable_type'}),
            'batch': forms.Select(attrs={'class': 'form-select', 'id': 'id_batch'}),
            'assigned_student': forms.Select(attrs={'class': 'form-select', 'id': 'id_assigned_student'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initially set empty queryset for students (will be populated based on batch)
        self.fields['assigned_student'].queryset = StudentProfile.objects.none()
        self.fields['assigned_student'].required = False
        self.fields['batch'].required = False
        self.fields['batch'].empty_label = "---------"
        
        # If batch is selected in POST data or initial data, filter students
        if 'batch' in self.data:
            try:
                batch_id = int(self.data.get('batch'))
                if batch_id:
                    self.fields['assigned_student'].queryset = StudentProfile.objects.filter(
                        batches__batch_id=batch_id,
                        batches__is_active=True,
                        status='active'
                    ).select_related('user').distinct().order_by('user__first_name', 'user__last_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.batch:
            # For editing existing deliverable
            self.fields['assigned_student'].queryset = StudentProfile.objects.filter(
                batches__batch_id=self.instance.batch.id,
                batches__is_active=True,
                status='active'
            ).select_related('user').distinct()
        
        # Add help texts
        self.fields['deliverable_type'].help_text = "Choose 'Batch-wide' for all students or 'Individual' for specific student"
        self.fields['file'].help_text = "Upload PDF, DOC, DOCX, ZIP (Max 50MB)"
        self.fields['batch'].help_text = "Select a batch to filter students for individual deliverables"
    
    def clean(self):
        cleaned_data = super().clean()
        deliverable_type = cleaned_data.get('deliverable_type')
        batch = cleaned_data.get('batch')
        assigned_student = cleaned_data.get('assigned_student')
        title = cleaned_data.get('title')
        description = cleaned_data.get('description')
        file = cleaned_data.get('file')
        
        # Validate title
        if not title:
            raise ValidationError('Title is required.')
        
        # Validate description
        if not description:
            raise ValidationError('Description is required.')
        
        # Validate file
        if not file and not self.instance.pk:
            raise ValidationError('File is required.')
        
        # Validate based on deliverable type
        if deliverable_type == 'batch':
            if not batch:
                raise ValidationError('Please select a batch for batch-wide deliverable.')
            if assigned_student:
                raise ValidationError('Cannot select a student for batch-wide deliverable.')
        
        elif deliverable_type == 'individual':
            if not assigned_student:
                raise ValidationError('Please select a student for individual deliverable.')
            
            # Verify student belongs to batch if batch is selected
            if batch and assigned_student:
                if not StudentBatch.objects.filter(
                    student=assigned_student, 
                    batch=batch, 
                    is_active=True
                ).exists():
                    raise ValidationError('The selected student does not belong to the selected batch.')
        
        return cleaned_data

class StudentProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = StudentProfile
        fields = ['phone', 'qualification', 'experience']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        student_profile = super().save(commit=False)
        user = student_profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            student_profile.save()
        
        return student_profile