from django.contrib import admin
from django.utils.html import format_html
from .models import (
    StudentProfile, Batch, StudentBatch, DailySession,
    Project, StudentProjectSubmission, Deliverable, StudentDeliverable
)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'qualification', 'status', 'joined_at']
    list_filter = ['status', 'joined_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['joined_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone',)
        }),
        ('Professional Details', {
            'fields': ('qualification', 'experience')
        }),
        ('Status', {
            'fields': ('status', 'joined_at')
        }),
    )

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'status', 'student_count', 'capacity_used']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def student_count(self, obj):
        return obj.students.filter(is_active=True).count()
    student_count.short_description = 'Enrolled Students'
    
    def capacity_used(self, obj):
        count = obj.students.filter(is_active=True).count()
        percentage = (count / obj.batch_capacity * 100) if obj.batch_capacity > 0 else 0
        return format_html(
            '<div style="width:100px; background:#f0f0f0;"><div style="width:{}%; background:#4CAF50; color:white; text-align:center;">{}/{}%</div></div>',
            percentage, count, obj.batch_capacity
        )
    capacity_used.short_description = 'Capacity Usage'

@admin.register(StudentBatch)
class StudentBatchAdmin(admin.ModelAdmin):
    list_display = ['student', 'batch', 'enrolled_on', 'is_active']
    list_filter = ['batch', 'is_active', 'enrolled_on']
    search_fields = ['student__user__username', 'student__user__email', 'batch__name']

@admin.register(DailySession)
class DailySessionAdmin(admin.ModelAdmin):
    list_display = ['batch', 'day_number', 'title', 'session_date', 'created_at']
    list_filter = ['batch', 'session_date']
    search_fields = ['title', 'topic']
    readonly_fields = ['created_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_number', 'batch_or_individual', 'due_date', 'status']
    list_filter = ['status', 'due_date', 'batch']
    search_fields = ['title', 'description']
    
    def batch_or_individual(self, obj):
        if obj.batch:
            return f"Batch: {obj.batch.name}"
        elif obj.assigned_student:
            return f"Student: {obj.assigned_student.user.get_full_name()}"
        return "Unknown"
    batch_or_individual.short_description = 'Assigned To'

@admin.register(StudentProjectSubmission)
class StudentProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'project', 'status', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['student__user__username', 'project__title']
    readonly_fields = ['submitted_at', 'reviewed_at']

@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ['title', 'batch', 'stage_number', 'created_at']
    list_filter = ['batch', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['stage_number', 'created_at']

@admin.register(StudentDeliverable)
class StudentDeliverableAdmin(admin.ModelAdmin):
    list_display = ['student', 'deliverable', 'is_downloaded', 'downloaded_at']
    list_filter = ['is_downloaded', 'assigned_at']
    search_fields = ['student__user__username', 'deliverable__title']
    readonly_fields = ['assigned_at', 'downloaded_at']