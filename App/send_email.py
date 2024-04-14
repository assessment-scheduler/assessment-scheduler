# import smtplib

# # Takes veryy long but works
# def send_mail(email):
#     smtp_server = "smtp-mail.outlook.com"
#     sender_email = 'vanessa.aubin@hotmail.com'
#     receiver_email = email
#     appPassword = 'urbskwoytvlmzowc'
#     message = 'This is a test email!'

#     # Send email
#     with smtplib.SMTP(smtp_server, 587) as server:
#         server.ehlo()
#         server.starttls()
#         server.login(sender_email, appPassword)
#         server.sendmail(sender_email, receiver_email, message)
#         server.close()     


    # Flask mail configs
    # app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USERNAME'] = 'vanessa.onica@gmail.com'
    # app.config['MAIL_PASSWORD'] = 'urbskwoytvlmzowc' # App Password used 
    # app.config['MAIL_USE_TLS'] = False
    # app.config['MAIL_USE_SSL'] = True        