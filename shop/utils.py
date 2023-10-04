import os
import base64
import io
import hashlib
import json

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse

import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from xhtml2pdf import pisa

from shop.models import  Order


def generate_invoice_to_send_email(request, pk):
    order = get_object_or_404(Order, id=pk)
    invoice_id = hashlib.sha1(str(order.id).encode()).hexdigest()

    total_amount = 0
    for item in order.order_items.all():
        total_amount += item.total_product_price

    # Generate the PDF as you did before
    template_path = 'product/invoice-template.html'  # Replace with your HTML template path
    template = get_template(template_path)
    context = {'order': order, 'invoice_id': invoice_id, 'total_amount': total_amount}
    html = template.render(context)
    pdf_file = io.BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)
    pdf_content = pdf_file.getvalue()

    # Store the PDF on the server
    pdf_filename = f'invoice_{order.id}.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    with open(pdf_path, 'wb') as pdf_file:
        pdf_file.write(pdf_content)

    # Create a SendGrid message
    message = Mail(
        from_email='saheerabcd3@gmail.com',  # Replace with your sender email
        to_emails=request.user.email,  # Replace with the recipient's email
        subject='Invoice for Order #' + str(order.id),
        plain_text_content='Please find attached the invoice for your order.',
        html_content='Please find attached the invoice for your order.'
    )

    # Attach the PDF using SendGrid's Attachment class
    attachment = Attachment()
    attachment.file_content = FileContent(base64.b64encode(pdf_content).decode())
    attachment.file_name = FileName('invoice.pdf')
    attachment.file_type = FileType('application/pdf')
    attachment.disposition = Disposition('attachment')

    message.attachment = attachment

    try:
        # Initialize the SendGrid client and send the email
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        sg.send(message)

        response_data = {
            "status": "success",
            "email": request.user.email
        }

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    except Exception as e:
        return HttpResponse(f'Failed to send invoice: {str(e)}')
