"""
Django management command to regenerate QR codes and PDFs for tickets.

Usage:
    python manage.py regenerate_tickets              # Regenerate all missing files
    python manage.py regenerate_tickets --force      # Force regenerate all files
    python manage.py regenerate_tickets --user=john  # Regenerate for specific user
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from tickets.models import Ticket
from tickets.utils import generate_qr_code, generate_pdf_ticket
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Regenerate QR codes and PDFs for tickets'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regenerate all files (not just missing ones)',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Regenerate tickets for specific user (by email or username)',
        )
        parser.add_argument(
            '--event',
            type=str,
            help='Regenerate tickets for specific event (by ID)',
        )
        parser.add_argument(
            '--ticket-id',
            type=str,
            help='Regenerate specific ticket (by UUID)',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        user_filter = options.get('user')
        event_filter = options.get('event')
        ticket_id = options.get('ticket_id')
        
        # Filter tickets
        tickets_qs = Ticket.objects.all()
        
        if ticket_id:
            tickets_qs = tickets_qs.filter(ticket_id=ticket_id)
        
        if user_filter:
            tickets_qs = tickets_qs.filter(
                Q(user__email=user_filter) | Q(user__username=user_filter)
            )
        
        if event_filter:
            tickets_qs = tickets_qs.filter(event_id=event_filter)
        
        if not force:
            # Only get tickets with missing files
            tickets_qs = tickets_qs.filter(Q(qr_code='') | Q(pdf_ticket=''))
        
        total = tickets_qs.count()
        
        if total == 0:
            self.stdout.write(
                self.style.WARNING('✓ No tickets to regenerate')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Processing {total} ticket(s)...\n')
        )
        
        qr_success = 0
        qr_errors = 0
        pdf_success = 0
        pdf_errors = 0
        
        for idx, ticket in enumerate(tickets_qs, 1):
            self.stdout.write(f'[{idx}/{total}] Ticket {ticket.ticket_number} ({ticket.user.email})')
            
            # Generate QR
            if force or not ticket.qr_code:
                try:
                    generate_qr_code(ticket)
                    self.stdout.write(f'  ✓ QR code generated')
                    qr_success += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ QR error: {str(e)}')
                    )
                    qr_errors += 1
            
            # Generate PDF
            if force or not ticket.pdf_ticket:
                try:
                    pdf_path = generate_pdf_ticket(ticket)
                    if pdf_path:
                        ticket.pdf_ticket = pdf_path
                        ticket.save(update_fields=['pdf_ticket', 'updated_at'])
                        self.stdout.write(f'  ✓ PDF generated')
                        pdf_success += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ PDF generation returned None')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ PDF error: {str(e)}')
                    )
                    pdf_errors += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('REGENERATION COMPLETE'))
        self.stdout.write('='*50)
        self.stdout.write(f'QR Codes:  {qr_success} ✓, {qr_errors} ✗')
        self.stdout.write(f'PDFs:      {pdf_success} ✓, {pdf_errors} ✗')
        self.stdout.write(f'Total:     {qr_success + pdf_success} files generated')
        
        if qr_errors + pdf_errors > 0:
            self.stdout.write(
                self.style.ERROR(f'\n⚠ {qr_errors + pdf_errors} error(s) occurred. Check logs.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ All files regenerated successfully!')
            )
