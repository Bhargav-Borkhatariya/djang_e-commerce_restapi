import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_activation_otp_email(user, otp):
    email_subject = f"Activation OTP for {user}"
    email_body = render_to_string("activation.html", {"user": user, "otp": otp})
    email = EmailMessage(email_subject, email_body, to=[user.email])
    email.content_subtype = "html"

    # Define a function to send email in a separate thread
    def send_email_thread(email):
        email.send()

    # Start a new thread to send email
    threading.Thread(target=send_email_thread, args=(email,)).start()


def send_forget_password_otp_email(user, otp):
    email_subject = f"Forget Password OTP for {user}"
    email_body = render_to_string("forget_pass.html", {"user": user, "otp": otp})
    email = EmailMessage(email_subject, email_body, to=[user.email])
    email.content_subtype = "html"

    # Define a function to send email in a separate thread
    def send_email_thread(email):
        email.send()

    # Start a new thread to send email
    threading.Thread(target=send_email_thread, args=(email,)).start()
