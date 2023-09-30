import pyotp
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def send_otp(request, email):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()

    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=1)
    request.session['otp_valid_date'] = str(valid_date)

    subject = 'Your OTP Verification Code'
    message = f'Your OTP code is: {otp}'
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
