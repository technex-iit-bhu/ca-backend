import smtplib 
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from django.conf import settings
import cloudinary.api

cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
)

try:
    SUPPORT_EMAIL = config("SUPPORT_EMAIL")
except:
    SUPPORT_EMAIL = "tech@technex.in"

try:
    LOGO_IMG = cloudinary.api.resource(config("LOGO_IMG"), format="png")
except Exception as e:
    LOGO_IMG = {
        "secure_url": ""
    }

def send_task_admin_comment_email(rec_email, username, admin_comment):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Admin Comment on Your Task"

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>An admin has  reviewed your submitted task and provided the following comment:</p>
            <br>
                <div style="background-color: #f2f2f2; padding: 10px;">
                    <p>{admin_comment}</p>
                </div>
            <p> Please review this feedback for any additional guidance or clarification.</p>
            <p>Should you have any questions or require further assistance, do not hesitate to contact our support team at {SUPPORT_EMAIL}.</p>
            <p>Best regards,</p>
            <p>CA Team - Technex'24</p>
        </body>
    </html>
    """
    body = html
    msg.attach(MIMEText(body, 'html'))
    send(rec_email, msg)

def send_task_submission_email(rec_email, username, task_name):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Task Submission Confirmation"

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>Thank you for submitting your task {task_name} to Technex'24. We are delighted to inform you that your task has been received and processed successfully.</p>
            <p>If you have any concerns or need further clarification, please feel free to reach out to us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,</p>
            <p>CA Team - Technex'24</p>
        </body>
    </html>
    """
    body = html
    msg.attach(MIMEText(body, 'html'))
    send(rec_email, msg)

def send_task_submission_verification_email(rec_email, username, task_name):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Task Submission Verification"

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>We are pleased to inform you that your task {task_name} has been successfully verified. Thank you for completing the task promptly.</p>
            <p>If you have any concerns or need further clarification, please feel free to reach out to us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,</p>
            <p>CA Team - Technex'24</p>
        </body>
    </html>
    """
    body = html
    msg.attach(MIMEText(body, 'html'))
    send(rec_email, msg)

def send(rec_email, msg):
    """
    Function to send verification email to the user 
    """
    msg = msg.as_string()   


    connection = smtplib.SMTP("smtp.gmail.com", port=587)
    connection.starttls()
    connection.ehlo_or_helo_if_needed()
    connection.login(config("EMAIL_HOST_USER"), config("EMAIL_HOST_PASSWORD"))
    connection.sendmail(config("EMAIL_HOST_USER"), rec_email, msg)
    connection.quit()
