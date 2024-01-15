from decouple import config
import smtplib
#todo: improve messages
def send_email_cnf_email(rec_email):
    msg=f"Subject:Your Technex account\n\nYour email has been verified. We will contact you shortly with further procedures."
    send(rec_email,msg)

def send_email_verif_email(rec_email,token):
    msg=f"Subject:Verify your Technex account\n\nPlease click on the following link to verify your email:\n\n{config('BACKEND_URL')}/auth/verifyemail/{token}"
    send(rec_email,msg)

def send_approved_email(rec_email):
    msg=f"Subject:Your Technex account\n\nYour account has been approved. You can now login to your account. \n\n CA Portal:  {config('FRONTEND_URL')}/"
    send(rec_email,msg)

def send_otp_email(rec_email,otp):
    msg=f"Subject:OTP for password reset\n\nYour OTP for resetting your password is {otp}.\n If you did not request this, ignore this mail and do not share your OTP."
    send(rec_email,msg)

def send(rec_email,msg):
    """
    Function to send verification email to the user 
    """
    
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=config("EMAIL_HOST_USER"), password=config("EMAIL_HOST_PASSWORD"))
        connection.sendmail(from_addr=config("EMAIL_HOST_USER"), to_addrs=rec_email,msg=msg)
        # connection.close()
    

