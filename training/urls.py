from django.urls import path
from . import views
from .views import *

app_name = 'training'

urlpatterns = [
    # Student URLs
    path('signup/', views.student_signup, name='signup'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/my-batch/', views.my_batch, name='my_batch'),
    path('student/sessions/', views.student_sessions, name='student_sessions'),
    path('student/projects/', views.student_projects, name='student_projects'),
    path('student/projects/<int:project_id>/submit/', views.submit_project, name='submit_project'),
    path('student/deliverables/', views.student_deliverables, name='student_deliverables'),
    path('student/deliverables/<int:deliverable_id>/download/', views.download_deliverable, name='download_deliverable'),
    path('student/profile/', views.student_profile_update, name='student_profile'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Student Management
    path('admin/students/', views.student_list, name='student_list'),
    path('admin/students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('admin/students/<int:student_id>/update-status/', views.update_student_status, name='update_student_status'),
    path('admin/students/batch/<int:student_batch_id>/remove/', views.remove_student_from_batch, name='remove_student_from_batch'),
    
    # Batch Management
    path('admin/batches/', views.batch_list, name='batch_list'),
    path('admin/batches/create/', views.batch_create, name='batch_create'),
    path('admin/batches/<int:batch_id>/edit/', views.batch_edit, name='batch_edit'),
    
    # Session Management
    path('admin/sessions/', views.session_list, name='session_list'),
    path('admin/sessions/create/', views.session_create, name='session_create'),
    path('admin/sessions/<int:session_id>/edit/', views.session_edit, name='session_edit'),
    
    # Project Management
    path('admin/projects/', views.project_list, name='project_list'),
    path('admin/projects/create/', views.project_create, name='project_create'),
    path('admin/projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    
    # Submissions
    path('admin/submissions/', views.project_submissions, name='project_submissions'),
    path('admin/submissions/<int:submission_id>/review/', views.review_submission, name='review_submission'),
    
    # Deliverables
    path('admin/deliverables/', views.deliverable_list, name='deliverable_list'),
    path('admin/deliverables/create/', views.deliverable_create, name='deliverable_create'),
    path('admin/sessions/next-day/<int:batch_id>/', views.get_next_day_number, name='get_next_day_number'),
    path('admin/projects/next-number/<int:batch_id>/', views.get_next_project_number, name='get_next_project_number'),
    path('admin/deliverables/get-students/<int:batch_id>/', views.get_students_by_batch, name='get_students_by_batch'),
    path('deliverable/<int:deliverable_id>/submit/', student_submit_deliverable, name='student_submit_deliverable'),
    path('deliverable/<int:deliverable_id>/detail/', student_deliverable_detail, name='student_deliverable_detail'),
    path('student-deliverable/<int:student_deliverable_id>/download/', student_download_approved_version, name='student_download_approved'),
    
    # Admin URLs
    path('admin/deliverables/pending/', pending_reviews, name='pending_reviews'),
    path('admin/deliverables/version/<int:version_id>/review/', review_deliverable_version, name='review_deliverable_version'),
    path('admin/student-deliverable/<int:student_deliverable_id>/', admin_student_deliverable_detail, name='admin_student_deliverable_detail'),
    path('admin/student-deliverable/<int:student_deliverable_id>/upload-version/', admin_upload_version, name='admin_upload_version'),
    path('admin/deliverables/all-submissions/', views.admin_all_student_deliverables, name='admin_all_student_deliverables'), 
]