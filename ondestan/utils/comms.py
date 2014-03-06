# coding=UTF-8
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

smtp_server = config.get_string_value('smtp_server')
smtp_port = config.get_int_value('smtp_port')
smtp_mail = config.get_string_value('smtp_mail')
smtp_password = config.get_string_value('smtp_password')

def send_mail(html, text, subject, destination):
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_mail
    msg['To'] = destination
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    server = SMTP(smtp_server, smtp_port)
    server.starttls()

    #Next, log in to the server
    server.login(smtp_mail, smtp_password)

    #Send the mail
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(smtp_mail, destination, msg.as_string())
    server.quit()