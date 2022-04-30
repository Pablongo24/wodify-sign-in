import os
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

port = 465  # for SSL

# Create a secure SSL contest
context = ssl.create_default_context()


def send_email(reservation_status, class_date, class_time, email_pablo=True, email_alex=False):
    """Send email alert, whether reservation was successful or not."""
    success_email_subject = f'Wodify class reserved for {class_date.strftime("%m/%d/%Y")}'
    success_email_body = MIMEText(
            f"The {class_time} class has been reserved for {class_date.strftime('%m/%d/%Y')}.\n"
            f"Double check your reservation at: https://app.wodify.com/"
        )
    failure_email_subject = 'Your Wodify class reservation failed'
    failure_email_body = MIMEText(
        'The registration failed. Please check https://app.wodify.com/" to reserve manually or check '
        'if you\'re already registered.'
    )

    if reservation_status:
        email_subject = success_email_subject
        email_body = success_email_body
    else:
        email_subject = failure_email_subject
        email_body = failure_email_body

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(os.environ.get("PABLO_GMAIL"), password=os.environ.get("GMAIL_APP_PW"))

        pablo_gmail = os.environ.get("PABLO_GMAIL")
        alex_gmail = os.environ.get("ALEX_GMAIL")
        message = email_body

        message['Subject'] = email_subject
        message['From'] = pablo_gmail

        if email_pablo:
            # Email Pablo
            message['To'] = pablo_gmail

            server.sendmail(pablo_gmail, pablo_gmail, message.as_string())

        if email_alex:
            # Email Alex
            message['To'] = alex_gmail
            server.sendmail(pablo_gmail, alex_gmail, message.as_string())


if __name__ == '__main__':
    send_email(reservation_status='success', class_time='Open Gym: 8:00 AM - 4:00 PM', class_date=datetime.today())
