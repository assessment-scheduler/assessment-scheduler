import smtplib
from email.mime.text import MIMEText

def send_mail(staff):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = ''
    password = ''
    message = f"<h3>Staff Registration Successful</h3><br><br><p>Dear {staff.firstName}, <br>you have successfully registered for the Assessment Scheduler Application."

    sender_email = 'email1@example.com'
    receiver_email = {staff.email}
    msg = MIMEText(message, 'html')
    msg['Subject'] = 'Registration Successful'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send email
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())