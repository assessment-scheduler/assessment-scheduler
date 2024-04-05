import smtplib

# Takes veryy long but works
def send_mail(email):
    smtp_server = 'smtp.gmail.com'
    sender_email = 'vanessa.onica@gmail.com'
    receiver_email = email
    appPassword = 'urbskwoytvlmzowc'
    message = 'This is a test email!'

    # Send email
    with smtplib.SMTP(smtp_server, 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, appPassword)
        server.sendmail(sender_email, receiver_email, message)
        server.close()