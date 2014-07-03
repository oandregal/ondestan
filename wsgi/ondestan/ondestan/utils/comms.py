# coding=UTF-8
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import TwilioRestClient

from ondestan.config import Config
import logging, sys

logger = logging.getLogger('ondestan')

# put your own credentials here
account_sid = Config.get_string_value('twilio.account_sid')
auth_token =Config.get_string_value('twilio.auth_token')
caller_nr = Config.get_string_value('twilio.caller_nr')
default_prefix = Config.get_string_value('twilio.default_prefix')

if Config.get_boolean_value('twilio.send_sms'):
    client = TwilioRestClient(account_sid, auth_token)
else:
    client = None

smtp_server = Config.get_string_value('smtp.server')
smtp_port = int(Config.get_string_value('smtp.port'))
smtp_mail = Config.get_string_value('smtp.mail')
smtp_password = Config.get_string_value('smtp.password')


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
    try:
        server.starttls()

        server.login(smtp_mail, smtp_password)

        server.sendmail(smtp_mail, destination, msg.as_string())
        logger.info("E-mail with subject '" + subject + "' has been sent to " +
                    "email " + destination)
    except Exception, e:
        logger.error("E-mail with subject '" + subject + "' couldn't be sent "
                     + "to email " + destination + " due to error "
                     + str(type(e)) + ":" + str(e))
    finally:
        server.quit()


def send_sms(text, number):
    if client != None:
        client.messages.create(
            to=number if number.startswith('+') else default_prefix + number,
            from_=caller_nr,
            body=text
        )
        logger.info("Sms '" + text + "' has been sent to number " + number)
    else:
        logger.info("Sms '" + text + "' has been processed but not sent to" +
                    " number " + number)
    return
