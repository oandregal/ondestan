# coding=UTF-8
from hashlib import sha512

from ..entities.user import User
from ..utils import comms
import logging

logger = logging.getLogger('ondestan')

def group_finder(login, request):
    user = User().queryObject().filter(User.login==login, User.activated==True).scalar()
    if ((user != None) and (user.role != None)):
        return ['role:' + user.role.name];
    return [];

def activate_user(loginhash):
    users = User().queryObject().all()
    for user in users:
        if sha512(user.login).hexdigest() == loginhash:
            logger.info('User ' + user.login + ' has been activated')
            user.activated = True
            user.save()

def check_login_request(request):
    return check_user_pass(request.params['login'], request.params['password'])

def check_user_pass(login, password):
    user = User().queryObject().filter(User.login==login, User.activated==True).scalar()
    if (user != None):
        return user.password == sha512(password).hexdigest()
    return False

def get_user_by_login(login):
    User().queryObject().filter(User.login==login).scalar()

def create_user(request):
    login = request.params['login']
    name = request.params['name']
    email = request.params['email']
    user = User().queryObject().filter(User.login==login).scalar()
    if (user != None):
        return False
    user = User()
    user.login = login
    user.name = name
    user.email = email
    user.phone = request.params['phone']
    user.activated = False
    user.password = sha512(request.params['password']).hexdigest()
    user.role_id = 2
    user.save()
    
    # Create the body of the message (a plain-text and an HTML version).
    url = request.route_url('activate_user', loginhash=sha512(login).hexdigest())
    text = "Hi " + name + "!\nPlease click the following link in order to activate your account:\n" + url
    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi """ + name + """!<br>
           Please click this <a href=\"""" + url + """\">link</a> in order to activate your account.
        </p>
      </body>
    </html>
    """
    
    comms.send_mail(html, text, 'Ondestán signup', email)
    
    return True