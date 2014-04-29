# coding=UTF-8
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import expandvars
from twilio.rest import TwilioRestClient

from ondestan.config import Config
import logging

logger = logging.getLogger('ondestan')

# put your own credentials here
account_sid = expandvars(Config.get_string_value('twilio.account_sid'))
auth_token = expandvars(Config.get_string_value('twilio.auth_token'))
caller_nr = expandvars(Config.get_string_value('twilio.caller_nr'))
default_prefix = expandvars(Config.get_string_value('twilio.default_prefix'))

# client = TwilioRestClient(account_sid, auth_token)

smtp_server = expandvars(Config.get_string_value('smtp.server'))
smtp_port = int(expandvars(Config.get_string_value('smtp.port')))
smtp_mail = expandvars(Config.get_string_value('smtp.mail'))
smtp_password = expandvars(Config.get_string_value('smtp.password'))


def send_mail(html, text, subject, destination):

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

    logger.info("E-mail with subject '" + subject + "' has been sent to email "
                + destination)


def send_sms(text, number):
    """client.messages.create(
        to=number if number.startswith('+') else default_prefix + number,
        from_=caller_nr,
        body=text
    )"""
    logger.info("Sms '" + text + "' has been sent to number " + number)
    return
