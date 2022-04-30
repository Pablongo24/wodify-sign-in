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
    email_subjects_and_bodies = {
        "success": {
            "subject": f'Wodify class reserved for {class_date.strftime("%m/%d/%Y")}',
            "body": f"The {class_time} class has been reserved for {class_date.strftime('%m/%d/%Y')}.\n"
                    f"Double check your reservation at: https://app.wodify.com/"
        },
        "already reserved": {
            "subject": f'Wodify class for {class_date.strftime("%m/%d/%Y")} was already reserved',
            "body": f"The {class_time} class was already reserved for {class_date.strftime('%m/%d/%Y')}.\n"
                    f"To double check your reservation, go to: https://app.wodify.com/"
        },
        "cannot reserve": {
            "subject": f'Cannot reserve Wodify class for {class_date.strftime("%m/%d/%Y")}',
            "body": f"Could not reserve the {class_time} class for {class_date.strftime('%m/%d/%Y')}.\n"
                    f"This is likely because the reservation isn't open yet. "
                    f"To confirm, please check: https://app.wodify.com/"
        },
        "there was a problem": {
            "subject": f'Problem trying to reserve Wodify class for {class_date.strftime("%m/%d/%Y")}',
            "body": f"There was a problem when trying to reserve the {class_time} class "
                    f"for {class_date.strftime('%m/%d/%Y')}.\n"
                    f"If you still want to reserve it, please do so manually at https://app.wodify.com/"
        }
    }

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(os.environ.get("PABLO_GMAIL"), password=os.environ.get("GMAIL_APP_PW"))

        pablo_gmail = os.environ.get("PABLO_GMAIL")
        alex_gmail = os.environ.get("ALEX_GMAIL")
        message = MIMEText(email_subjects_and_bodies[reservation_status]['body'])

        message['Subject'] = email_subjects_and_bodies[reservation_status]['subject']
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
