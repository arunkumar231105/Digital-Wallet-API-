import smtplib
from email.message import EmailMessage


EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "arunkumarjuswani12@gmail.com"
EMAIL_PASSWORD = "fnwo uyvd mayw ftlj"


def send_transfer_email(to_email: str, amount: str):
    msg = EmailMessage()
    msg["Subject"] = "Wallet Credit Notification"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(f"You have received {amount} $ in your wallet.")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def send_freeze_email(to_email: str):
    msg = EmailMessage()
    msg["Subject"] = "Account Freeze Notification"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content("Your account has been frozen by admin.")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def send_unfreeze_email(to_email: str):
    msg = EmailMessage()
    msg["Subject"] = "Account Reactivation Notification"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content("Your account has been reactivated by admin.")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def send_admin_deposit_email(to_email: str, amount: str):
    msg = EmailMessage()
    msg["Subject"] = "Admin Deposit Notification"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(f"Admin has deposited {amount} into your wallet.")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
