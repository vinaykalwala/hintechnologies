from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import StudentProfile, Deliverable, StudentDeliverable, StudentBatch

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Create StudentProfile when User is created"""
    if created:
        StudentProfile.objects.get_or_create(
            user=instance,
            defaults={
                'phone': '',
                'qualification': '',
                'experience': '',
                'status': 'active'
            }
        )

@receiver(post_save, sender=Deliverable)
def assign_deliverable_to_students(sender, instance, created, **kwargs):
    """Auto-assign deliverable to students based on type"""
    if created:
        if instance.deliverable_type == 'batch' and instance.batch:
            # Assign to all active students in the batch
            batch_students = StudentBatch.objects.filter(
                batch=instance.batch,
                is_active=True
            ).select_related('student')
            
            for student_batch in batch_students:
                StudentDeliverable.objects.get_or_create(
                    student=student_batch.student,
                    deliverable=instance
                )
        elif instance.deliverable_type == 'individual' and instance.assigned_student:
            # Assign to individual student only
            StudentDeliverable.objects.get_or_create(
                student=instance.assigned_student,
                deliverable=instance
            )

@receiver(post_save, sender=StudentBatch)
def assign_existing_deliverables_to_student(sender, instance, created, **kwargs):
    """When student is assigned to batch, assign all existing batch deliverables"""
    if created:
        # Assign all existing batch deliverables for this batch
        deliverables = Deliverable.objects.filter(
            batch=instance.batch,
            deliverable_type='batch'
        )
        for deliverable in deliverables:
            StudentDeliverable.objects.get_or_create(
                student=instance.student,
                deliverable=deliverable
            )