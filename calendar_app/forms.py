from django import forms
from .models import CalendarEvent


class CalendarEventForm(forms.ModelForm):
    """Formulário para criar/editar eventos do calendário"""

    class Meta:
        model = CalendarEvent
        fields = [
            'title',
            'description',
            'event_type',
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'all_day',
            'location',
            'collection',
            'color',
            'sync_enabled',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Título do Evento'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Descrição do evento...'
            }),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-input',
                'type': 'time'
            }),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Local do evento'
            }),
            'collection': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color'
            }),
            'sync_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'event_type': 'Tipo de Evento',
            'start_date': 'Data de Início',
            'start_time': 'Hora de Início',
            'end_date': 'Data de Término',
            'end_time': 'Hora de Término',
            'all_day': 'Evento de dia inteiro',
            'location': 'Local',
            'collection': 'Coleção Relacionada',
            'color': 'Cor do Evento',
            'sync_enabled': 'Sincronizar com Google Calendar',
        }
