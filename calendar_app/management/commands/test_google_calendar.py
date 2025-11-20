"""
Django management command to test Google Calendar API authentication
"""
from django.core.management.base import BaseCommand
from calendar_app.google_calendar import GoogleCalendarService


class Command(BaseCommand):
    help = 'Test Google Calendar API authentication and connection'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando teste da API do Google Calendar...'))
        self.stdout.write('')

        try:
            # Initialize the service
            self.stdout.write('1. Inicializando serviço...')
            service = GoogleCalendarService()

            if not service.service:
                self.stdout.write(self.style.ERROR('✗ Falha ao autenticar com Google Calendar'))
                self.stdout.write('')
                self.stdout.write('Verifique se:')
                self.stdout.write('  - O arquivo credentials.json existe na raiz do projeto')
                self.stdout.write('  - As credenciais são válidas')
                self.stdout.write('  - Você tem acesso à internet')
                return

            self.stdout.write(self.style.SUCCESS('✓ Serviço autenticado com sucesso!'))
            self.stdout.write('')

            # Test calendar access
            self.stdout.write('2. Testando acesso ao calendário...')
            try:
                calendar = service.service.calendars().get(
                    calendarId=service.calendar_id
                ).execute()

                self.stdout.write(self.style.SUCCESS('✓ Acesso ao calendário confirmado!'))
                self.stdout.write(f'  - Nome do calendário: {calendar.get("summary", "N/A")}')
                self.stdout.write(f'  - ID do calendário: {service.calendar_id}')
                self.stdout.write('')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erro ao acessar calendário: {e}'))
                return

            # Test listing events
            self.stdout.write('3. Testando listagem de eventos...')
            try:
                from datetime import datetime, timedelta

                now = datetime.utcnow().isoformat() + 'Z'
                events_result = service.service.events().list(
                    calendarId=service.calendar_id,
                    timeMin=now,
                    maxResults=5,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                events = events_result.get('items', [])

                self.stdout.write(self.style.SUCCESS(f'✓ Encontrados {len(events)} eventos futuros'))

                if events:
                    self.stdout.write('')
                    self.stdout.write('Próximos eventos:')
                    for event in events:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        self.stdout.write(f'  - {start}: {event["summary"]}')

                self.stdout.write('')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erro ao listar eventos: {e}'))
                return

            # Success summary
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('TESTE CONCLUÍDO COM SUCESSO!'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write('')
            self.stdout.write('A integração com Google Calendar está funcionando corretamente.')
            self.stdout.write('Agora os eventos criados no sistema serão sincronizados automaticamente!')
            self.stdout.write('')

        except Exception as e:
            self.stdout.write(self.style.ERROR('=' * 60))
            self.stdout.write(self.style.ERROR(f'ERRO: {str(e)}'))
            self.stdout.write(self.style.ERROR('=' * 60))
            self.stdout.write('')
            import traceback
            self.stdout.write(traceback.format_exc())
