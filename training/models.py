from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
import os

# Student Profile Model
class StudentProfile(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('placed', 'Placed'),
        ('inactive', 'Inactive'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=200)
    experience = models.TextField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.status}"
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

# Batch Model
class Batch(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField(help_text="Total number of training days")
    batch_capacity = models.PositiveIntegerField(default=30)
    number_of_projects = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Batches"
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('training:batch_detail', kwargs={'pk': self.pk})
    
    def enrolled_students_count(self):
        # Use the related_name 'students' from StudentBatch model
        return self.students.filter(is_active=True).count()
    
    def is_capacity_available(self):
        return self.enrolled_students_count() < self.batch_capacity
    
    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date')

# Student Batch Assignment
class StudentBatch(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='batches')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='students')  # related_name='students'
    enrolled_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'batch']
        ordering = ['-enrolled_on']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.batch.name}"
    
    def save(self, *args, **kwargs):
        if not self.batch.is_capacity_available():
            raise ValidationError(f"Batch {self.batch.name} has reached maximum capacity.")
        super().save(*args, **kwargs)

class DailySession(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='sessions')
    day_number = models.PositiveIntegerField(blank=True, null=True)  # Allow null for auto-generation
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=300)
    session_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    recording_link = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['batch', 'day_number']
        ordering = ['batch', 'day_number']
    
    def __str__(self):
        return f"Day {self.day_number}: {self.title} - {self.batch.name}"
    
    def save(self, *args, **kwargs):
        # Auto-increment day number if not provided
        if not self.day_number:
            last_session = DailySession.objects.filter(batch=self.batch).order_by('-day_number').first()
            if last_session:
                self.day_number = last_session.day_number + 1
            else:
                self.day_number = 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('training:session_detail', kwargs={'pk': self.pk})

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, related_name='projects')
    assigned_student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='individual_projects')
    due_date = models.DateField()
    project_number = models.PositiveIntegerField(help_text="Project number within batch")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['batch', 'project_number']
        unique_together = ['batch', 'project_number']
    
    def __str__(self):
        if self.batch:
            return f"{self.batch.name} - Project {self.project_number}: {self.title}"
        elif self.assigned_student:
            return f"Individual: {self.title} - {self.assigned_student.user.get_full_name()}"
        return f"Project: {self.title}"
    
    def clean(self):
        if self.batch and self.assigned_student:
            raise ValidationError("Project cannot be assigned to both a batch and an individual student.")
        if not self.batch and not self.assigned_student:
            raise ValidationError("Project must be assigned to either a batch or an individual student.")
        
        # Validate max projects for batch (only for NEW projects)
        if self.batch and not self.pk:  # Only check for new projects
            active_projects_count = Project.objects.filter(
                batch=self.batch
            ).exclude(status='completed').count()
            
            if active_projects_count >= self.batch.number_of_projects:
                raise ValidationError(
                    f'This batch already has {self.batch.number_of_projects} active/pending projects. '
                    f'Complete or archive existing projects before adding more.'
                )
    
    def get_visible_students(self):
        """Returns queryset of students who can see this project"""
        # Only show projects that are NOT pending
        if self.status == 'pending':
            return StudentProfile.objects.none()
        
        if self.batch:
            return StudentProfile.objects.filter(batches__batch=self.batch, batches__is_active=True)
        elif self.assigned_student:
            return StudentProfile.objects.filter(id=self.assigned_student.id)
        return StudentProfile.objects.none()
    
    def save(self, *args, **kwargs):
        # Auto-increment project number ONLY for NEW projects (no primary key yet)
        if not self.pk:  # Check if this is a new project
            if self.batch and not self.project_number:
                last_project = Project.objects.filter(batch=self.batch).order_by('-project_number').first()
                if last_project:
                    self.project_number = last_project.project_number + 1
                else:
                    self.project_number = 1
        
        # Validate max projects before saving (only for new projects)
        if not self.pk and self.batch:
            self.clean()
        
        super().save(*args, **kwargs)
# Student Project Submission
def submission_zip_path(instance, filename):
    return f'submissions/batch_{instance.project.batch.id}/student_{instance.student.user.id}/{filename}'

class StudentProjectSubmission(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='project_submissions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)
    zip_file = models.FileField(upload_to=submission_zip_path, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    admin_feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    class Meta:
        unique_together = ['student', 'project']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.project.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if self.status in ['approved', 'rejected'] and not self.reviewed_at:
            self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)

# Deliverable Model
def deliverable_file_path(instance, filename):
    """Generate file path for deliverables"""
    # For batch deliverables
    if instance.deliverable_type == 'batch' and instance.batch:
        return f'deliverables/batch_{instance.batch.id}/{filename}'
    # For individual deliverables
    elif instance.deliverable_type == 'individual' and instance.assigned_student:
        return f'deliverables/student_{instance.assigned_student.user.id}/{filename}'
    # Fallback for any other case
    else:
        return f'deliverables/others/{filename}'

class Deliverable(models.Model):
    TYPE_CHOICES = [
        ('batch', 'Batch-wide'),
        ('individual', 'Individual Student'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, related_name='deliverables')
    assigned_student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='individual_deliverables')
    deliverable_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='batch')
    file = models.FileField(upload_to=deliverable_file_path)
    stage_number = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_deliverables')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.deliverable_type == 'individual' and self.assigned_student:
            return f"Individual: {self.title} - {self.assigned_student.user.get_full_name()}"
        elif self.deliverable_type == 'batch' and self.batch:
            return f"Batch: {self.title} - {self.batch.name}"
        return f"Deliverable: {self.title}"
    
    def save(self, *args, **kwargs):
        # Set stage number for new deliverables
        if not self.pk:
            if self.deliverable_type == 'batch' and self.batch:
                last_deliverable = Deliverable.objects.filter(
                    batch=self.batch, 
                    deliverable_type='batch'
                ).order_by('-stage_number').first()
                self.stage_number = (last_deliverable.stage_number + 1) if last_deliverable else 1
            elif self.deliverable_type == 'individual' and self.assigned_student:
                last_deliverable = Deliverable.objects.filter(
                    assigned_student=self.assigned_student,
                    deliverable_type='individual'
                ).order_by('-stage_number').first()
                self.stage_number = (last_deliverable.stage_number + 1) if last_deliverable else 1
        
        super().save(*args, **kwargs)

class StudentDeliverable(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='deliverables')
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='student_records')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_downloaded = models.BooleanField(default=False)
    downloaded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'deliverable']
        ordering = ['deliverable__stage_number']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.deliverable.title} ({'Downloaded' if self.is_downloaded else 'Not Downloaded'})"
    
    def mark_downloaded(self):
        if not self.is_downloaded:
            self.is_downloaded = True
            self.downloaded_at = timezone.now()
            self.save()