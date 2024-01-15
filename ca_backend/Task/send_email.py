import smtplib 
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

try:
    SUPPORT_EMAIL = config("SUPPORT_EMAIL")
except:
    SUPPORT_EMAIL = "tech@technex.in"

LOGO_FILE_PATH = "./ca_backend/logo/asset.png"

with open(LOGO_FILE_PATH, 'rb') as fp:
    IMAGE = MIMEImage(fp.read())
    IMAGE.add_header('Content-ID', '<logo>')
    IMAGE.add_header('Content-Disposition', 'inline')  # Set the Content-Disposition header to "inline"

def send_task_admin_comment_email(rec_email, username, admin_comment, connection: smtplib.SMTP = None):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Admin Comment on Your Task"

    # Use images and style the email
    if IMAGE:
        msg.attach(IMAGE)
    else:
        with open(LOGO_FILE_PATH, 'rb') as fp:
            img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<logo>')
        img.add_header('Content-Disposition', 'inline')  # Set the Content-Disposition header to "inline"
        msg.attach(img)

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><img src="cid:logo" alt="logo" border="0" width="200" height="200"></center>
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
    text = msg.as_string()
    send(rec_email, text, connection)

def send_task_submission_email(rec_email, username, task_name, connection: smtplib.SMTP = None):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Task Submission Confirmation"

    # Use images and style the email
    if IMAGE:
        msg.attach(IMAGE)
    else:
        with open(LOGO_FILE_PATH, 'rb') as fp:
            img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<logo>')
        img.add_header('Content-Disposition', 'inline')
        msg.attach(img)

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><img src="cid:logo" alt="logo" border="0" width="200" height="200"></center>
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
    text = msg.as_string()
    send(rec_email, text, connection)

def send_task_submission_verification_email(rec_email, username, task_name, connection: smtplib.SMTP = None):
    msg = MIMEMultipart()
    msg['From'] = config("EMAIL_HOST_USER")
    msg['To'] = rec_email
    msg['Subject'] = "Technex'24 - Task Submission Verification"

    # Use images and style the email
    if IMAGE:
        msg.attach(IMAGE)
    else:
        with open(LOGO_FILE_PATH, 'rb') as fp:
            img = MIMEImage(fp.read())
        img.add_header('Content-ID', '<logo>')
        img.add_header('Content-Disposition', 'inline')
        msg.attach(img)

    html = f"""\
    <html>
        <head></head>
        <body>
        <center><img src="cid:logo" alt="logo" border="0" width="200" height="200"></center>
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
    text = msg.as_string()
    send(rec_email, text, connection)

def send(rec_email, msg, connection: smtplib.SMTP = None):
    """
    Function to send verification email to the user 
    """
    if connection:
        connection.sendmail(config("EMAIL_HOST_USER"), rec_email, msg)
    else:
        connection = smtplib.SMTP("smtp.gmail.com", port=587)
        connection.starttls()
        connection.login(config("EMAIL_HOST_USER"), config("EMAIL_HOST_PASSWORD"))
        connection.sendmail(config("EMAIL_HOST_USER"), rec_email, msg)