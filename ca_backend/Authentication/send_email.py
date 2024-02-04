from decouple import config
import smtplib
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


#todo: improve messages
def send_email_cnf_email(rec_email, username):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Email Verification Successful"
    # Use images and style the email

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>Great news! Your email address has been successfully verified for your Technex'24 account. Please wait for our admins to verify your account. Once that is done we will contact you and you will be able to log in to your account.</p>
            <br>
            If you have any additional questions or if there's anything else we can assist you with, feel free to reach out to our support team at {SUPPORT_EMAIL}.

            Thank you for being a part of Technex'24!
            <br>
            <p>Best regards,</p>
            <p>CA Team - Technex'24</p>

        </body>
    </html>
    """
    body = html
    msg.attach(MIMEText(body, 'html'))
    send(rec_email, msg)


def send_email_verif_email(rec_email, token, username):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Email Verification"
    # Use images and style the email
    
    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>Congratulations! Your account on Technex'24 has been successfully created. Please click on the following button to confirm and activate your account</p>
            <br>
            <center><a href="{config('BACKEND_URL')}/auth/verifyemail/{token}/"><button style="background-color: #4CAF50; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; cursor: pointer;">Verify Email</button></a></center>
            <br>
            <p>If you encounter any issues or have any questions, feel free to reach out to our support team at {SUPPORT_EMAIL}.</p>
            <p>Best regards,</p>
            <p>CA Team - Technex'24</p>

            PS: If you are unable to click the button, copy and paste the following link in your browser: {config('BACKEND_URL')}/auth/verifyemail/{token}/
        </body>
    </html>
    """
    body = html
    msg.attach(MIMEText(body, 'html'))
    send(rec_email, msg)

def send_approved_email(rec_email, username):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Account Approved"
    # Use images and style the email
    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>We are pleased to inform you that your Technex'24 account has been successfully verified. Thank you for completing the verification process promptly.</p>
            <br>
            <p>If you encounter any issues or have any questions, feel free to reach out to our support team at {SUPPORT_EMAIL}.</p>
            <p>Best regards,</p>
            <p>CA Team - Technex'24</p>
        </body>
    </html>
    """
    body = html
    msg.attach(MIMEText(body, 'html'))
    send(rec_email, msg)

def send_otp_email(rec_email,otp, username):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Password Reset OTP"
   
    html = f"""\
    <html>
        <head></head>
        <body>
        <center><a href="{config('FRONTEND_URL')}"><img src="{LOGO_IMG['secure_url']}" alt="Technex '24" border="0" width="200" height="200" draggable="false"></a></center>
            <h3>Dear {username},</h3>
            <br>
            <p>Here is your OTP for verification:</p>
            <br>
            <center><h1>{otp}</h1></center>
            <br>
            <p>Do not share this OTP with anyone. If you did not request this OTP, please ignore this email.</p>
            <p>If you encounter any issues or have any questions, feel free to reach out to our support team at {SUPPORT_EMAIL}.</p>
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
    

