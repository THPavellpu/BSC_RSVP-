from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from .models import Ticket
from .utils import generate_qr_code, generate_pdf_ticket
import logging

logger = logging.getLogger(__name__)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'user', 'event', 'status', 'qr_status', 'pdf_status', 'created_at', 'regenerate_link']
    list_filter = ['status', 'event', 'created_at']
    search_fields = ['user__full_name', 'user__email', 'event__title', 'ticket_id']
    readonly_fields = ['ticket_id', 'created_at', 'updated_at', 'qr_preview', 'file_status']
    actions = ['regenerate_tickets']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_id', 'user', 'event', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_preview'),
        }),
        ('PDF Ticket', {
            'fields': ('pdf_ticket',),
        }),
        ('File Status', {
            'fields': ('file_status',),
            'classes': ('collapse',)
        }),
    )
    
    def qr_status(self, obj):
        """Display QR code status with colored indicator."""
        if obj.qr_code:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Generated</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Missing</span>'
        )
    qr_status.short_description = 'QR Status'
    
    def pdf_status(self, obj):
        """Display PDF status with colored indicator."""
        if obj.pdf_ticket:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Generated</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Missing</span>'
        )
    pdf_status.short_description = 'PDF Status'
    
    def qr_preview(self, obj):
        """Show QR code preview."""
        if obj.qr_code:
            try:
                return format_html(
                    '<img src="{}" width="200" height="200" style="border: 2px solid #ccc; padding: 5px; border-radius: 5px; object-fit: contain;">',
                    obj.qr_code.url
                )
            except Exception as e:
                return format_html(
                    '<div style="color: red;">Error loading QR code: {}</div>',
                    str(e)
                )
        return format_html(
            '<div style="padding: 20px; border: 2px dashed #ccc; text-align: center; border-radius: 5px;">No QR code</div>'
        )
    qr_preview.short_description = 'QR Code Preview'
    
    def file_status(self, obj):
        """Detailed file status information."""
        status_html = '<div style="font-family: monospace; white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 3px;">'
        status_html += f'Ticket ID: {obj.ticket_id}\n'
        status_html += f'QR Code: {obj.qr_code or "NOT GENERATED"}\n'
        status_html += f'PDF Ticket: {obj.pdf_ticket or "NOT GENERATED"}\n'
        status_html += '</div>'
        return format_html(status_html)
    file_status.short_description = 'File Status Info'
    
    def regenerate_link(self, obj):
        """Quick action link to regenerate files."""
        if not obj.qr_code or not obj.pdf_ticket:
            return format_html(
                '<a class="button" href="{}?ticket_id={}">🔄 Regenerate</a>',
                reverse('admin:tickets_ticket_changelist'),
                obj.pk
            )
        return '✓'
    regenerate_link.short_description = 'Action'
    
    def regenerate_tickets(self, request, queryset):
        """Admin action to regenerate QR and PDF files for selected tickets."""
        count = 0
        errors = 0
        
        for ticket in queryset:
            try:
                # Regenerate QR code
                if not ticket.qr_code:
                    try:
                        generate_qr_code(ticket)
                        logger.info(f"✓ QR regenerated for ticket {ticket.ticket_id}")
                    except Exception as e:
                        logger.error(f"✗ QR regeneration failed: {str(e)}")
                        errors += 1
                
                # Regenerate PDF
                if not ticket.pdf_ticket:
                    try:
                        pdf_path = generate_pdf_ticket(ticket)
                        if pdf_path:
                            ticket.pdf_ticket = pdf_path
                            ticket.save(update_fields=['pdf_ticket', 'updated_at'])
                            logger.info(f"✓ PDF regenerated for ticket {ticket.ticket_id}")
                        else:
                            logger.warning(f"⚠ PDF regeneration returned None")
                            errors += 1
                    except Exception as e:
                        logger.error(f"✗ PDF regeneration failed: {str(e)}")
                        errors += 1
                
                count += 1
                
            except Exception as e:
                logger.error(f"✗ Regeneration failed for ticket {ticket.ticket_id}: {str(e)}", exc_info=True)
                errors += 1
        
        message = f"Successfully regenerated {count} ticket(s)"
        if errors > 0:
            message += f" with {errors} error(s). Check logs for details."
        
        self.message_user(request, message)
    
    regenerate_tickets.short_description = "🔄 Regenerate QR codes and PDFs for selected tickets"
