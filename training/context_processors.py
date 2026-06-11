from .models import DeliverableVersion

def pending_deliverable_reviews(request):
    pending_count = DeliverableVersion.objects.filter(
        status='pending',
        submitter_type='student'
    ).count()

    return {
        'pending_deliverable_reviews_count': pending_count
    }