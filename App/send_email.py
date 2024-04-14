from flask import current_app as app
from flask_mail import Mail, Message
from mailbox import Message

def send_mail():
    #  Flask mail configs
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'vanessa.onica@gmail.com'
    app.config['MAIL_DEFAULT_SENDER'] = 'vanessa.onica@gmail.com'
    app.config['MAIL_PASSWORD'] = 'urbskwoytvlmzowc' # App Password used 
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True 
    mail = Mail(app)

    receiver_email = 'vanessa.aubin@hotmail.com'
    
    msg = Message()
    msg.subject = 'Test Email!'
    msg.body = 'Successful Registration'
    msg.recipients = ['vanessa.aubin@hotmail.com']
    mail.send(msg)
    return print('Success')
   