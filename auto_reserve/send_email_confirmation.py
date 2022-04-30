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


def send_email(email_pablo=True, email_alex=False):
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(os.environ.get("PABLO_GMAIL"), password=os.environ.get("GMAIL_APP_PW"))

        pablo_gmail = os.environ.get("PABLO_GMAIL")
        alex_gmail = os.environ.get("ALEX_GMAIL")
        message = MIMEText(
            f"You have a class reservation for {datetime.today().strftime('%m/%d/%Y')}.\n"
            f"Double check your reservation at: https://app.wodify.com/"
        )

        message['Subject'] = 'You have a new Wodify class reservation'
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
    send_email()
