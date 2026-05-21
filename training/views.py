from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
from .models import (
    StudentProfile, Batch, StudentBatch, DailySession,
    Project, StudentProjectSubmission, Deliverable, StudentDeliverable
)
from .forms import (
    StudentSignupForm, BatchForm, StudentBatchForm, DailySessionForm,
    ProjectForm, ProjectSubmissionForm, ReviewSubmissionForm,
    DeliverableForm, StudentProfileUpdateForm
)

# Helper functions
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

def get_student_profile(user):
    try:
        return user.student_profile
    except StudentProfile.DoesNotExist:
        return None

def student_signup(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        # Check if user is student or admin
        try:
            if hasattr(request.user, 'student_profile'):
                return redirect('training:student_dashboard')
            elif request.user.is_superuser or request.user.is_staff:
                return redirect('hin:dashboard')
            else:
                return redirect('hin:dashboard')
        except:
            return redirect('hin:dashboard')
    
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        
        # Debug: Print form errors to console
        if not form.is_valid():
            print("Form errors:", form.errors)
        
        if form.is_valid():
            try:
                # Save the form and create user + profile
                student_profile = form.save()
                
                # Success message
                messages.success(
                    request, 
                    f'Account created successfully for {student_profile.user.username}! Please login to continue.'
                )
                
                # Redirect to login page
                return redirect('hin:login')
                
            except IntegrityError as e:
                # Handle duplicate entry errors
                if 'username' in str(e):
                    messages.error(request, 'Username already exists. Please choose a different username.')
                elif 'email' in str(e):
                    messages.error(request, 'Email already registered. Please use a different email.')
                else:
                    messages.error(request, f'Database error: {str(e)}')
                    
            except Exception as e:
                # Handle any other errors
                messages.error(request, f'Error creating account: {str(e)}')
                print(f"Signup error: {str(e)}")  # Debug print
                
                # If user was created but profile failed, clean up
                if 'user' in locals():
                    try:
                        user = User.objects.get(username=form.cleaned_data.get('username'))
                        user.delete()
                    except:
                        pass
        else:
            # Form is invalid - show specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentSignupForm()
    
    return render(request, 'training/signup.html', {'form': form})

@login_required
def student_dashboard(request):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    # Get current batch
    current_batch = StudentBatch.objects.filter(
        student=student_profile, 
        is_active=True
    ).select_related('batch').first()
    
    context = {
        'student_profile': student_profile,
        'current_batch': current_batch.batch if current_batch else None,
    }
    
    # If student has a batch, get additional data
    if current_batch:
        batch = current_batch.batch
        
        # Get sessions
        sessions = DailySession.objects.filter(batch=batch)[:5]
        
        # Get projects
        batch_projects = Project.objects.filter(batch=batch)
        individual_projects = Project.objects.filter(assigned_student=student_profile)
        projects = batch_projects | individual_projects
        
        # Get deliverables
        deliverables = StudentDeliverable.objects.filter(
            student=student_profile,
            deliverable__batch=batch
        ).select_related('deliverable')
        
        # Calculate progress
        total_projects = projects.count()
        completed_projects = StudentProjectSubmission.objects.filter(
            student=student_profile,
            status='approved'
        ).count()
        
        context.update({
            'sessions': sessions,
            'projects': projects[:5],
            'deliverables': deliverables,
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'progress_percentage': int((completed_projects / total_projects * 100)) if total_projects > 0 else 0,
        })
    
    return render(request, 'training/student/dashboard.html', context)

@login_required
def my_batch(request):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    student_batch = StudentBatch.objects.filter(
        student=student_profile, 
        is_active=True
    ).select_related('batch').first()
    
    if not student_batch:
        messages.info(request, 'You are not assigned to any batch yet.')
        return render(request, 'training/student/no_batch.html')
    
    batch = student_batch.batch
    
    # Calculate progress
    total_projects = Project.objects.filter(batch=batch).count()
    completed_projects = StudentProjectSubmission.objects.filter(
        student=student_profile,
        project__batch=batch,
        status='approved'
    ).count()
    
    total_deliverables = Deliverable.objects.filter(batch=batch).count()
    downloaded_deliverables = StudentDeliverable.objects.filter(
        student=student_profile,
        deliverable__batch=batch,
        is_downloaded=True
    ).count()
    
    context = {
        'batch': batch,
        'student_batch': student_batch,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'project_progress': int((completed_projects / total_projects * 100)) if total_projects > 0 else 0,
        'total_deliverables': total_deliverables,
        'downloaded_deliverables': downloaded_deliverables,
        'deliverable_progress': int((downloaded_deliverables / total_deliverables * 100)) if total_deliverables > 0 else 0,
    }
    
    return render(request, 'training/student/my_batch.html', context)

@login_required
def student_sessions(request):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    student_batch = StudentBatch.objects.filter(
        student=student_profile, 
        is_active=True
    ).select_related('batch').first()
    
    if not student_batch:
        messages.info(request, 'You are not assigned to any batch yet.')
        return redirect('training:student_dashboard')
    
    sessions = DailySession.objects.filter(batch=student_batch.batch).order_by('day_number')
    
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'training/student/sessions.html', {
        'sessions': page_obj,
        'batch': student_batch.batch,
    })

@login_required
def student_projects(request):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    student_batch = StudentBatch.objects.filter(
        student=student_profile, 
        is_active=True
    ).select_related('batch').first()
    
    # Get only ACTIVE projects (exclude pending)
    batch_projects = []
    if student_batch:
        batch_projects = Project.objects.filter(
            batch=student_batch.batch,
            status__in=['active', 'completed']
        )
    
    # Get individual projects (only active ones)
    individual_projects = Project.objects.filter(
        assigned_student=student_profile,
        status__in=['active', 'completed']
    )
    
    # Combine projects
    projects = list(batch_projects) + list(individual_projects)
    
    for project in projects:
        try:
            submission = StudentProjectSubmission.objects.get(student=student_profile, project=project)
            project.submission_status = submission.status
            project.submission = submission
            # Check if actually submitted (has content)
            if submission.status == 'submitted' and not submission.github_link and not submission.live_link and not submission.zip_file:
                project.submission_status = 'not_started'  # Treat empty as not started
        except StudentProjectSubmission.DoesNotExist:
            project.submission_status = 'not_started'
            project.submission = None
    
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'training/student/projects.html', {
        'projects': page_obj,
        'student_batch': student_batch,
    })
@login_required
def submit_project(request, project_id):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    project = get_object_or_404(Project, id=project_id)
    
    # Check if student can access this project
    visible_students = project.get_visible_students()
    if student_profile not in visible_students:
        return HttpResponseForbidden("You don't have access to this project.")
    
    # Check if already submitted and approved
    try:
        submission = StudentProjectSubmission.objects.get(student=student_profile, project=project)
        if submission.status in ['approved']:
            messages.warning(request, 'This project has already been approved. Cannot submit again.')
            return redirect('training:student_projects')
        elif submission.status in ['under_review']:
            messages.warning(request, 'Your submission is already under review. Please wait for feedback.')
            return redirect('training:student_projects')
    except StudentProjectSubmission.DoesNotExist:
        submission = None
    
    if request.method == 'POST':
        if submission:
            form = ProjectSubmissionForm(request.POST, request.FILES, instance=submission)
        else:
            form = ProjectSubmissionForm(request.POST, request.FILES)
        
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student_profile
            submission.project = project
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()
            submission.save()
            messages.success(request, 'Project submitted successfully! Waiting for review.')
            return redirect('training:student_projects')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        if submission:
            form = ProjectSubmissionForm(instance=submission)
        else:
            form = ProjectSubmissionForm()
    
    return render(request, 'training/student/submit_project.html', {
        'form': form,
        'project': project,
        'submission': submission,
    })

@login_required
def student_deliverables(request):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    # Get all deliverables assigned to this student (both batch and individual)
    deliverables = StudentDeliverable.objects.filter(
        student=student_profile
    ).select_related(
        'deliverable', 
        'deliverable__batch', 
        'deliverable__assigned_student'
    ).order_by('deliverable__stage_number', '-deliverable__created_at')
    
    # Separate batch and individual for better display
    batch_deliverables = deliverables.filter(deliverable__deliverable_type='batch')
    individual_deliverables = deliverables.filter(deliverable__deliverable_type='individual')
    
    paginator = Paginator(deliverables, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'training/student/deliverables.html', {
        'deliverables': page_obj,
        'batch_deliverables': batch_deliverables,
        'individual_deliverables': individual_deliverables,
        'total_count': deliverables.count(),
    })

@login_required
def download_deliverable(request, deliverable_id):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    student_deliverable = get_object_or_404(StudentDeliverable, 
        id=deliverable_id, 
        student=student_profile
    )
    
    # Mark as downloaded
    student_deliverable.mark_downloaded()
    
    # Serve the file
    response = HttpResponse(student_deliverable.deliverable.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{student_deliverable.deliverable.file.name.split("/")[-1]}"'
    return response

@login_required
def student_profile_update(request):
    student_profile = get_student_profile(request.user)
    
    if not student_profile:
        messages.warning(request, 'Student profile not found.')
        return redirect('hin:dashboard')
    
    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('training:student_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentProfileUpdateForm(instance=student_profile)
    
    return render(request, 'training/student/profile.html', {'form': form})

# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_students = StudentProfile.objects.count()
    active_students = StudentProfile.objects.filter(status='active').count()
    total_batches = Batch.objects.count()
    running_batches = Batch.objects.filter(status='running').count()
    total_projects = Project.objects.count()
    
    # Count only actual submissions (not empty ones)
    pending_submissions = StudentProjectSubmission.objects.filter(
        status='submitted'
    ).filter(
        Q(github_link__isnull=False) | 
        Q(live_link__isnull=False) | 
        Q(zip_file__isnull=False)
    ).exclude(
        Q(github_link='') & Q(live_link='') & Q(zip_file='')
    ).count()
    
    total_deliverables = Deliverable.objects.count()
    
    recent_students = StudentProfile.objects.select_related('user').all()[:5]
    recent_batches = Batch.objects.all()[:5]
    
    # Get only actual pending reviews
    pending_reviews = StudentProjectSubmission.objects.filter(
        status='submitted'
    ).filter(
        Q(github_link__isnull=False) | 
        Q(live_link__isnull=False) | 
        Q(zip_file__isnull=False)
    ).exclude(
        Q(github_link='') & Q(live_link='') & Q(zip_file='')
    ).select_related('student', 'project')[:5]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_batches': total_batches,
        'running_batches': running_batches,
        'total_projects': total_projects,
        'pending_submissions': pending_submissions,
        'total_deliverables': total_deliverables,
        'recent_students': recent_students,
        'recent_batches': recent_batches,
        'pending_reviews': pending_reviews,
    }
    
    return render(request, 'training/admin/dashboard.html', context)
    
@login_required
@user_passes_test(is_admin)
def student_list(request):
    students = StudentProfile.objects.select_related('user').all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        students = students.filter(status=status_filter)
    
    # Filter by batch
    batch_filter = request.GET.get('batch')
    if batch_filter:
        students = students.filter(batches__batch_id=batch_filter, batches__is_active=True)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Annotate with batch info
    students = students.annotate(
        current_batch_name=F('batches__batch__name'),
        current_batch_id=F('batches__batch__id')
    )
    
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    batches = Batch.objects.filter(status__in=['upcoming', 'running'])
    
    return render(request, 'training/admin/students/list.html', {
        'students': page_obj,
        'status_filter': status_filter,
        'batch_filter': batch_filter,
        'search_query': search_query,
        'batches': batches,
        'status_choices': StudentProfile.STATUS_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
def student_detail(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    student_batches = StudentBatch.objects.filter(student=student).select_related('batch')
    submissions = StudentProjectSubmission.objects.filter(student=student).select_related('project')[:10]
    deliverables = StudentDeliverable.objects.filter(student=student).select_related('deliverable')[:10]
    
    # Available batches for assignment
    available_batches = Batch.objects.exclude(
        status='completed'
    ).exclude(
        status='cancelled'
    ).exclude(
        id__in=student_batches.values('batch_id')
    )
    
    if request.method == 'POST':
        form = StudentBatchForm(request.POST)
        if form.is_valid():
            student_batch = form.save(commit=False)
            student_batch.student = student
            student_batch.save()
            
            # Auto-assign deliverables for this batch
            deliverables = Deliverable.objects.filter(batch=student_batch.batch)
            for deliverable in deliverables:
                StudentDeliverable.objects.get_or_create(
                    student=student,
                    deliverable=deliverable
                )
            
            messages.success(request, f'Student assigned to {student_batch.batch.name} successfully!')
            return redirect('training:student_detail', student_id=student.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentBatchForm()
        form.fields['batch'].queryset = available_batches
    
    return render(request, 'training/admin/students/detail.html', {
        'student': student,
        'student_batches': student_batches,
        'submissions': submissions,
        'deliverables': deliverables,
        'form': form,
        'available_batches': available_batches,
    })

@login_required
@user_passes_test(is_admin)
def update_student_status(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(StudentProfile.STATUS_CHOICES):
            student.status = new_status
            student.save()
            messages.success(request, f'Student status updated to {student.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('training:student_detail', student_id=student.id)

@login_required
@user_passes_test(is_admin)
def remove_student_from_batch(request, student_batch_id):
    student_batch = get_object_or_404(StudentBatch, id=student_batch_id)
    student_id = student_batch.student.id
    batch_name = student_batch.batch.name
    
    if request.method == 'POST':
        student_batch.delete()
        messages.success(request, f'Student removed from {batch_name}')
    
    return redirect('training:student_detail', student_id=student_id)

@login_required
@user_passes_test(is_admin)
def batch_list(request):
    batches = Batch.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        batches = batches.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        batches = batches.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Annotate with stats
    batches = batches.annotate(
        student_count=Count('students', filter=Q(students__is_active=True))
    )
    
    paginator = Paginator(batches, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'training/admin/batches/list.html', {
        'batches': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Batch.STATUS_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
def batch_create(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save()
            messages.success(request, f'Batch "{batch.name}" created successfully!')
            return redirect('training:batch_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BatchForm()
    
    return render(request, 'training/admin/batches/form.html', {
        'form': form,
        'title': 'Create Batch',
    })

@login_required
@user_passes_test(is_admin)
def batch_edit(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, f'Batch "{batch.name}" updated successfully!')
            return redirect('training:batch_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BatchForm(instance=batch)
    
    return render(request, 'training/admin/batches/form.html', {
        'form': form,
        'title': 'Edit Batch',
        'batch': batch,
    })

@login_required
@user_passes_test(is_admin)
def session_list(request):
    sessions = DailySession.objects.select_related('batch').all()
    
    # Filter by batch
    batch_filter = request.GET.get('batch')
    if batch_filter:
        sessions = sessions.filter(batch_id=batch_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        sessions = sessions.filter(
            Q(title__icontains=search_query) |
            Q(topic__icontains=search_query)
        )
    
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    batches = Batch.objects.all()
    
    return render(request, 'training/admin/sessions/list.html', {
        'sessions': page_obj,
        'batch_filter': batch_filter,
        'search_query': search_query,
        'batches': batches,
    })

@login_required
@user_passes_test(is_admin)
def session_create(request):
    if request.method == 'POST':
        form = DailySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user
            
            # Auto-increment day number if not provided
            if not session.day_number:
                last_session = DailySession.objects.filter(batch=session.batch).order_by('-day_number').first()
                if last_session:
                    session.day_number = last_session.day_number + 1
                else:
                    session.day_number = 1
            
            session.save()
            messages.success(request, f'Session "{session.title}" created successfully! Day {session.day_number}')
            return redirect('training:session_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Get batch_id from GET parameter
        batch_id = request.GET.get('batch')
        initial_data = {}
        
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id)
                last_session = DailySession.objects.filter(batch=batch).order_by('-day_number').first()
                
                if last_session:
                    next_day = last_session.day_number + 1
                else:
                    next_day = 1
                
                initial_data = {
                    'batch': batch,
                    'day_number': next_day,  # This will display in the field
                }
                
            except Batch.DoesNotExist:
                pass
        
        form = DailySessionForm(initial=initial_data)
    
    return render(request, 'training/admin/sessions/form.html', {
        'form': form,
        'title': 'Create Session',
    })

@login_required
@user_passes_test(is_admin)
def session_edit(request, session_id):
    session = get_object_or_404(DailySession, id=session_id)
    
    if request.method == 'POST':
        form = DailySessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, f'Session "{session.title}" updated successfully!')
            return redirect('training:session_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DailySessionForm(instance=session)
    
    return render(request, 'training/admin/sessions/form.html', {
        'form': form,
        'title': 'Edit Session',
        'session': session,
    })

@login_required
@user_passes_test(is_admin)
def project_list(request):
    projects = Project.objects.select_related('batch', 'assigned_student').all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter == 'batch':
        projects = projects.filter(batch__isnull=False)
    elif type_filter == 'individual':
        projects = projects.filter(assigned_student__isnull=False)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        projects = projects.filter(title__icontains=search_query)
    
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'training/admin/projects/list.html', {
        'projects': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'status_choices': Project.STATUS_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            
            # Auto-increment project number if not provided
            if project.batch and not project.project_number:
                last_project = Project.objects.filter(batch=project.batch).order_by('-project_number').first()
                if last_project:
                    project.project_number = last_project.project_number + 1
                else:
                    project.project_number = 1
            
            project.save()
            messages.success(request, f'Project "{project.title}" created successfully! Project #{project.project_number}')
            return redirect('training:project_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Auto-populate next project number if batch is selected
        initial_data = {}
        batch_id = request.GET.get('batch')
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id)
                last_project = Project.objects.filter(batch=batch).order_by('-project_number').first()
                next_number = (last_project.project_number + 1) if last_project else 1
                
                # Check if batch has reached its limit
                active_projects = Project.objects.filter(batch=batch).exclude(status='completed').count()
                if active_projects >= batch.number_of_projects:
                    messages.warning(request, f'This batch has reached its project limit ({batch.number_of_projects}). Cannot add more projects.')
                else:
                    initial_data = {
                        'batch': batch,
                        'project_number': next_number,
                    }
                    messages.info(request, f'Next project number for this batch will be {next_number}')
            except Batch.DoesNotExist:
                pass
        
        form = ProjectForm(initial=initial_data)
    
    return render(request, 'training/admin/projects/form.html', {
        'form': form,
        'title': 'Create Project',
    })

@login_required
@user_passes_test(is_admin)
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            # Save the project - preserve the original project_number and batch
            updated_project = form.save()
            messages.success(request, f'Project "{updated_project.title}" updated successfully!')
            return redirect('training:project_list')
        else:
            messages.error(request, 'Please correct the errors below.')
            print("Form errors:", form.errors)  # Debug print
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'training/admin/projects/form.html', {
        'form': form,
        'title': 'Edit Project',
        'project': project,
        'is_edit': True,
    })

@login_required
@user_passes_test(is_admin)
def project_submissions(request):
    # Get only submissions that have actual content
    submissions = StudentProjectSubmission.objects.select_related('student', 'project', 'student__user').all()
    
    # Filter out empty submissions (where nothing was submitted)
    submissions = submissions.filter(
        Q(github_link__isnull=False) | 
        Q(live_link__isnull=False) | 
        Q(zip_file__isnull=False)
    ).exclude(
        Q(github_link='') & Q(live_link='') & Q(zip_file='')
    )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    # Filter by project
    project_filter = request.GET.get('project')
    if project_filter:
        submissions = submissions.filter(project_id=project_filter)
    
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    projects = Project.objects.all()
    
    return render(request, 'training/admin/submissions/list.html', {
        'submissions': page_obj,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'projects': projects,
        'status_choices': StudentProjectSubmission.STATUS_CHOICES,
    })

@login_required
@user_passes_test(is_admin)
def review_submission(request, submission_id):
    submission = get_object_or_404(StudentProjectSubmission, id=submission_id)
    
    if request.method == 'POST':
        form = ReviewSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, f'Submission reviewed and marked as {submission.get_status_display()}')
            return redirect('training:project_submissions')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewSubmissionForm(instance=submission)
    
    return render(request, 'training/admin/submissions/review.html', {
        'form': form,
        'submission': submission,
    })

from django.http import JsonResponse
from django.db.models import Q

@login_required
@user_passes_test(is_admin)
def deliverable_create(request):
    if request.method == 'POST':
        form = DeliverableForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                deliverable = form.save(commit=False)
                deliverable.created_by = request.user
                deliverable.save()
                
                # Assign to students based on type
                if deliverable.deliverable_type == 'batch':
                    # Assign to all active students in the batch
                    batch_students = StudentBatch.objects.filter(
                        batch=deliverable.batch,
                        is_active=True
                    ).select_related('student')
                    
                    assigned_count = 0
                    for student_batch in batch_students:
                        StudentDeliverable.objects.get_or_create(
                            student=student_batch.student,
                            deliverable=deliverable
                        )
                        assigned_count += 1
                    
                    messages.success(
                        request, 
                        f'Deliverable "{deliverable.title}" created and assigned to {assigned_count} students in batch {deliverable.batch.name}!'
                    )
                else:
                    # Assign to individual student only
                    StudentDeliverable.objects.get_or_create(
                        student=deliverable.assigned_student,
                        deliverable=deliverable
                    )
                    messages.success(
                        request, 
                        f'Deliverable "{deliverable.title}" created and assigned to {deliverable.assigned_student.user.get_full_name()}!'
                    )
                
                return redirect('training:deliverable_list')
                
            except Exception as e:
                messages.error(request, f'Error creating deliverable: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DeliverableForm()
    
    return render(request, 'training/admin/deliverables/form.html', {
        'form': form,
        'title': 'Upload Deliverable',
    })

@login_required
@user_passes_test(is_admin)
def get_students_by_batch(request, batch_id):
    """AJAX endpoint to get students for a specific batch"""
    try:
        students = StudentProfile.objects.filter(
            batches__batch_id=batch_id,
            batches__is_active=True,
            status='active'
        ).select_related('user').distinct().order_by('user__first_name', 'user__last_name')
        
        student_list = [{
            'id': student.id,
            'name': student.user.get_full_name() or student.user.username,
            'email': student.user.email,
            'phone': student.phone
        } for student in students]
        
        return JsonResponse({
            'success': True,
            'students': student_list,
            'count': len(student_list)
        })
    except Batch.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Batch not found'
        }, status=404)

@login_required
@user_passes_test(is_admin)
def deliverable_list(request):
    deliverables = Deliverable.objects.select_related('batch', 'assigned_student').all()
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        deliverables = deliverables.filter(deliverable_type=type_filter)
    
    # Filter by batch
    batch_filter = request.GET.get('batch')
    if batch_filter:
        deliverables = deliverables.filter(batch_id=batch_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        deliverables = deliverables.filter(title__icontains=search_query)
    
    paginator = Paginator(deliverables, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    batches = Batch.objects.all()
    
    return render(request, 'training/admin/deliverables/list.html', {
        'deliverables': page_obj,
        'type_filter': type_filter,
        'batch_filter': batch_filter,
        'search_query': search_query,
        'batches': batches,
    })


from django.http import JsonResponse

@login_required
@user_passes_test(is_admin)
def get_next_day_number(request, batch_id):
    """AJAX endpoint to get the next day number for a batch"""
    try:
        batch = Batch.objects.get(id=batch_id)
        last_session = DailySession.objects.filter(batch=batch).order_by('-day_number').first()
        
        if last_session:
            next_day = last_session.day_number + 1
        else:
            next_day = 1
        
        return JsonResponse({
            'next_day': next_day,
            'batch_name': batch.name,
            'total_sessions': DailySession.objects.filter(batch=batch).count()
        })
    except Batch.DoesNotExist:
        return JsonResponse({'error': 'Batch not found'}, status=404)

@login_required
@user_passes_test(is_admin)
def get_next_project_number(request, batch_id):
    """AJAX endpoint to get the next project number for a batch"""
    try:
        batch = Batch.objects.get(id=batch_id)
        last_project = Project.objects.filter(batch=batch).order_by('-project_number').first()
        
        if last_project:
            next_number = last_project.project_number + 1
        else:
            next_number = 1
        
        # Calculate remaining capacity
        active_projects = Project.objects.filter(batch=batch).exclude(status='completed').count()
        remaining_capacity = batch.number_of_projects - active_projects
        
        return JsonResponse({
            'next_number': next_number,
            'active_projects': active_projects,
            'max_projects': batch.number_of_projects,
            'remaining_capacity': remaining_capacity,
            'batch_name': batch.name
        })
    except Batch.DoesNotExist:
        return JsonResponse({'error': 'Batch not found'}, status=404)