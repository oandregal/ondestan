# coding=UTF-8
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ondestan.utils import Config


def send_mail(html, text, subject, destination):

    smtp_server = Config.get_string_value('smtp.server')
    smtp_port = Config.get_int_value('smtp.port')
    smtp_mail = Config.get_string_value('smtp.mail')
    smtp_password = Config.get_string_value('smtp.password')

    # Create message container - the correct MIME type is multipart/alternative
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_mail
    msg['To'] = destination

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain', 'UTF-8')
    part2 = MIMEText(html, 'html', 'UTF-8')

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
    # sendmail function takes 3 arguments:
    # sender's address
    # recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(smtp_mail, destination, msg.as_string())
    server.quit()
