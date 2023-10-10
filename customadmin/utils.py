from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def send_user_refund_mail(request, amount, email):

    subject = 'Male Fashion Amount Refunded'
    message = f'Your order had been cancelled and the amount {amount} is refunded to your wallet.'
    from_email = 'saheerabcd3@gmail.com'  # Replace with your sender email address
    recipient_list = [email]

    msg = Mail(
        from_email=from_email,
        to_emails=recipient_list,
        subject=subject,
        plain_text_content=message
    )

    try:
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(msg)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
