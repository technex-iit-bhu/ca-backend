from decouple import config
import smtplib

def send_verification_email(rec_email, token):
    """
    Function to send verification email to the user 
    """
    msg=f"Subject:Your Technex account\n\nOur team will verify your account shortly, after which you will be able to login to your account."


    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=config("EMAIL_HOST_USER"), password=config("EMAIL_HOST_PASSWORD"))
        connection.sendmail(from_addr=config("EMAIL_HOST_USER"), to_addrs=rec_email,msg=msg)
        connection.close()
    


