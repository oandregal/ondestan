# coding=UTF-8
from pyramid.httpexceptions import (
    HTTPFound
    )

from pyramid.view import (
    view_config,
    forbidden_view_config
    )

from pyramid.security import (
    remember,
    forget
    )

from .cow import Cow
from .plot import Plot
from .user import User
from .security import check_login_request, get_user_login, check_permission, activate_user
from hashlib import sha512
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        if check_login_request(request):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        )

@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    message = ''
    login = ''
    name = ''
    email = ''
    phone = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        name = request.params['name']
        email = request.params['email']
        phone = request.params['phone']
        user = User().queryObject().filter(User.login==login).scalar()
        if (user == None):
            user = User()
            user.login = login
            user.name = name
            user.email = email
            user.phone = phone
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
            
            send_mail(html, text, 'Ondestán signup', email)
            raise HTTPFound(request.route_url("signup_success"))
        message = 'Login is already in use. Please choose a different one.'

    return dict(
        message = message,
        url = request.application_url + '/signup',
        login = login,
        name = name,
        email = email,
        phone = phone,
        )

@view_config(route_name='signup_success', renderer='templates/signupSuccess.pt')
def signup_success(request):
    return dict()

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('login'),
                     headers = headers)

@view_config(route_name='activate_user')
def activate_usr(request):
    loginhash = request.matchdict['loginhash']
    activate_user(loginhash)
    return HTTPFound(location = request.route_url('login'))

@view_config(route_name='map', renderer='templates/simpleViewer.pt',
             permission='view')
def viewer(request):
    return dict(project= 'Ondestán',
                user_id=get_user_login(request),
                can_edit=check_permission('edit', request),
                is_admin=check_permission('admin', request))

@view_config(route_name='default')
def default(request):
    raise HTTPFound(request.route_url("map"))

@view_config(route_name='json_points', renderer='json',
             permission='view')
def json_points(request):
    geojson = []
    if (check_permission('admin', request)):
        cows = Cow().queryObject().all()
        for cow in cows:
            geojson.append({
            "type": "Feature",
            "properties": {
                "name": cow.name,
                "battery_level": cow.battery_level,
                "owner": cow.user.login,
                "outside": cow.outside,
                "popup": cow.name + " (" + str(cow.battery_level) + "%), property of " + cow.user.login
            },
            "geometry": eval(cow.geojson)
            });
    else:
        user_id = get_user_login(request)
        cows = Cow().queryObject().filter(Cow.user.has(login=user_id)).all()
        for cow in cows:
            geojson.append({
            "type": "Feature",
            "properties": {
                "name": cow.name,
                "battery_level": cow.battery_level,
                "owner": cow.user.login,
                "outside": cow.outside,
                "popup": cow.name + " (" + str(cow.battery_level) + "%)"
            },
            "geometry": eval(cow.geojson)
            });
    return geojson;

@view_config(route_name='json_polygons', renderer='json',
             permission='view')
def json_polygons(request):
    geojson = []
    if (check_permission('admin', request)):
        plots = Plot().queryObject().all()
        for plot in plots:
            geojson.append({
            "type": "Feature",
            "properties": {
                "name": plot.name,
                "owner": plot.user.login,
                "popup": plot.name + " property of " + plot.user.login
            },
            "geometry": eval(plot.geojson)
            });
    else:
        user_id = get_user_login(request)
        plots = Plot().queryObject().filter(Plot.user.has(login=user_id)).all()
        for plot in plots:
            geojson.append({
            "type": "Feature",
            "properties": {
                "name": plot.name,
                "owner": plot.user.login,
                "popup": plot.name
            },
            "geometry": eval(plot.geojson)
            });
    return geojson;

def send_mail(html, text, subject, destination):
    
    # me == my email address
    # you == recipient's email address
    origin = ""
    password = ""
    serverURL = 'smtp.gmail.com'
    server_port = 587
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = origin
    msg['To'] = destination
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    server = SMTP(serverURL, server_port)
    server.starttls()

    #Next, log in to the server
    server.login(origin, password)

    #Send the mail
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(origin, destination, msg.as_string())
    server.quit()
    
