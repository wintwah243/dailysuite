from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import Note
from .forms import NoteForm


@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).order_by('-created_at')

    # Get date range for last 7 days
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    # Calculate notes created in last 7 days
    notes_last_7_days = Note.objects.filter(
        user=request.user,
        created_at__date__gte=week_ago
    )

    # Count by day for the chart
    notes_by_day = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        count = Note.objects.filter(
            user=request.user,
            created_at__date=day
        ).count()
        notes_by_day.append(count)

    # Get notes count by tag/category
    tags_data = []
    if hasattr(Note, 'tag'):
        tag_counts = Note.objects.filter(user=request.user).values('tag').annotate(
            count=Count('tag')
        ).order_by('-count')

        for tag in tag_counts:
            tags_data.append({
                'tag': tag['tag'] if tag['tag'] else 'Uncategorized',
                'count': tag['count']
            })
    else:
        # Fallback if tag field doesn't exist
        tags_data = [
            {'tag': 'Personal', 'count': notes.filter(content__icontains='personal').count()},
            {'tag': 'Work', 'count': notes.filter(content__icontains='work').count()},
            {'tag': 'Ideas', 'count': notes.filter(content__icontains='idea').count()},
            {'tag': 'Important', 'count': notes.filter(content__icontains='important').count()},
        ]

    # Calculate statistics
    this_week_count = Note.objects.filter(
        user=request.user,
        created_at__date__gte=week_ago
    ).count()

    # Check if pinned field exists
    if hasattr(Note, 'pinned'):
        important_count = notes.filter(pinned=True).count()
    else:
        important_count = notes.filter(
            Q(content__icontains='important') |
            Q(title__icontains='important')
        ).count()

    # Check if tag field exists for work notes count
    if hasattr(Note, 'tag'):
        work_count = notes.filter(tag='work').count()
    else:
        work_count = notes.filter(
            Q(content__icontains='work') |
            Q(title__icontains='work')
        ).count()

    # Get notes for calendar (last 30 days with notes)
    calendar_start = today - timedelta(days=30)
    notes_for_calendar = Note.objects.filter(
        user=request.user,
        created_at__date__gte=calendar_start
    ).values_list('created_at__date', flat=True).distinct()

    # Convert to string format
    calendar_days_with_notes = [
        date.strftime('%Y-%m-%d') for date in notes_for_calendar
    ]

    context = {
        'notes': notes,
        'total_notes': notes.count(),
        'this_week_count': this_week_count,
        'important_count': important_count,
        'work_count': work_count,
        'notes_by_day': notes_by_day,
        'tags_data': tags_data,
        'calendar_days_with_notes': calendar_days_with_notes,
        'week_days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }

    return render(request, 'notes/note_list.html', context)


@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user

            # Handle custom fields from modal
            tag = request.POST.get('tag', 'personal')
            if hasattr(note, 'tag'):
                note.tag = tag

            pinned = request.POST.get('pinned', False)
            if hasattr(note, 'pinned'):
                note.pinned = True if pinned == 'on' else False

            note.save()
            return redirect('note_list')
    else:
        form = NoteForm()

    return render(request, 'notes/note_form.html', {'form': form})


@login_required
def note_update(request, id):
    note = get_object_or_404(Note, id=id, user=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            updated_note = form.save(commit=False)

            # Handle custom fields from modal
            tag = request.POST.get('tag', 'personal')
            if hasattr(updated_note, 'tag'):
                updated_note.tag = tag

            pinned = request.POST.get('pinned', False)
            if hasattr(updated_note, 'pinned'):
                updated_note.pinned = True if pinned == 'on' else False

            updated_note.save()
            return redirect('note_list')
    else:
        form = NoteForm(instance=note)

    return render(request, 'notes/note_form.html', {'form': form})


@login_required
def note_delete(request, id):
    note = get_object_or_404(Note, id=id, user=request.user)

    if request.method == 'POST':
        note.delete()
        return redirect('note_list')

    return render(request, 'notes/note_confirm_delete.html', {'note': note})


# for calendar data
@login_required
def get_calendar_notes(request, date):

    try:
        target_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    notes = Note.objects.filter(
        user=request.user,
        created_at__date=target_date
    ).values('id', 'title', 'content', 'created_at')

    notes_list = list(notes)

    return JsonResponse({
        'date': date,
        'notes': notes_list,
        'count': len(notes_list)
    })