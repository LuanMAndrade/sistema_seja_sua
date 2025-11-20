from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
import calendar
from .models import CalendarEvent
from .forms import CalendarEventForm
from .google_calendar import GoogleCalendarService


@login_required
def calendar_view(request):
    """Main calendar view - monthly display"""
    # Get month and year from query params, default to current
    today = datetime.now()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Calculate previous and next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Get events for this month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

    events = CalendarEvent.objects.filter(
        start_date__gte=first_day,
        start_date__lte=last_day
    ).select_related('collection')

    # Organize events by date
    events_by_date = {}
    for event in events:
        date_key = event.start_date.day
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    context = {
        'calendar': cal,
        'month': month,
        'year': year,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today,
        'events_by_date': events_by_date,
    }
    return render(request, 'calendar_app/calendar.html', context)


@login_required
def event_create(request):
    """Create a new calendar event"""
    # Get date from query params if provided
    selected_date = request.GET.get('date')

    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save()

            # Sync with Google Calendar if enabled
            if event.sync_enabled:
                try:
                    service = GoogleCalendarService()
                    service.sync_event(event)
                    messages.success(request, f'Evento "{event.title}" criado e sincronizado com Google Calendar!')
                except Exception as e:
                    messages.warning(request, f'Evento criado, mas houve erro ao sincronizar: {str(e)}')
            else:
                messages.success(request, f'Evento "{event.title}" criado com sucesso!')

            return redirect('calendar_app:calendar_view')
    else:
        initial_data = {}
        if selected_date:
            try:
                initial_data['start_date'] = datetime.strptime(selected_date, '%Y-%m-%d').date()
            except:
                pass
        form = CalendarEventForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Novo Evento',
        'action': 'Criar',
    }
    return render(request, 'calendar_app/event_form.html', context)


@login_required
def event_edit(request, pk):
    """Edit an existing calendar event"""
    event = get_object_or_404(CalendarEvent, pk=pk)

    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()

            # Sync with Google Calendar if enabled
            if event.sync_enabled:
                try:
                    service = GoogleCalendarService()
                    service.sync_event(event)
                    messages.success(request, f'Evento "{event.title}" atualizado e sincronizado!')
                except Exception as e:
                    messages.warning(request, f'Evento atualizado, mas houve erro ao sincronizar: {str(e)}')
            else:
                messages.success(request, f'Evento "{event.title}" atualizado com sucesso!')

            return redirect('calendar_app:calendar_view')
    else:
        form = CalendarEventForm(instance=event)

    context = {
        'form': form,
        'title': f'Editar Evento: {event.title}',
        'action': 'Salvar',
        'event': event,
    }
    return render(request, 'calendar_app/event_form.html', context)


@login_required
def event_delete(request, pk):
    """Delete a calendar event"""
    event = get_object_or_404(CalendarEvent, pk=pk)

    if request.method == 'POST':
        # Delete from Google Calendar if synced
        if event.google_event_id and event.sync_enabled:
            try:
                service = GoogleCalendarService()
                service.delete_event(event.google_event_id)
            except Exception as e:
                messages.warning(request, f'Erro ao remover do Google Calendar: {str(e)}')

        event_title = event.title
        event.delete()
        messages.success(request, f'Evento "{event_title}" removido com sucesso!')
        return redirect('calendar_app:calendar_view')

    context = {
        'event': event,
    }
    return render(request, 'calendar_app/event_confirm_delete.html', context)


@login_required
def event_detail(request, pk):
    """View event details (AJAX endpoint)"""
    event = get_object_or_404(CalendarEvent, pk=pk)

    data = {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'event_type': event.get_event_type_display(),
        'start_date': event.start_date.strftime('%Y-%m-%d'),
        'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
        'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else None,
        'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
        'all_day': event.all_day,
        'location': event.location,
        'collection': event.collection.name if event.collection else None,
        'color': event.color or '#c9a961',
        'sync_enabled': event.sync_enabled,
    }

    return JsonResponse(data)
