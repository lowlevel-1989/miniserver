#
# Vinicio Valubena
#
# python3 -m venv env
# source env/bin/activate
# pip install -r requirements.txt
# FLASK_ENV=development flask run --debugger
# or
# podman run --rm -it --network host formatcom/miniserver --port 5000

import socket
import time

from uuid import uuid4

from flask import Flask
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import make_response

from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
# python -c 'import os; print(os.urandom(16))'
app.secret_key = b'[SECRET_KEY_HERE]'

# signer cookie session
signer = URLSafeTimedSerializer(
                app.secret_key, 'salt-cookie-session')

# helpers
_body_html = '''
    <br/>
    <pre>
        hostname: {hostname}
        server:   {server_ip}:{server_port}
        client:   {client_ip}:{client_port}
    </pre>
    {response}
'''

_body_text = '''
    hostname: {hostname}
    server:   {server_ip}:{server_port}
    client:   {client_ip}:{client_port}
    {response}
'''

def patch_response(response, _body=_body_html):
    return make_response(_body.format(**{
        'hostname':                    socket.gethostname(),
        'server_ip':                   request.server[0],
        'server_port':                 request.server[1],
        'client_ip':      request.environ['REMOTE_ADDR'],
        'client_port':    request.environ['REMOTE_PORT'],
        'response':                            response,
    }))

# session [server side]
_session = {}

# flask router
@app.route('/')
def index():

    # default text
    if request.accept_mimetypes['*/*'] == 1:

        response = patch_response('''
        You are not logged in.

        - login, client side
        $ curl -v -X POST -d 'username=vinicio' --cookie-jar - http://{server_ip}:{server_port}{login}
        $ curl -v --cookie 'session=aaaa.bb.cccc' http://{server_ip}:{server_port}

        - login, server side
        $ curl -v -X POST -d 'username=vinicio' --cookie-jar - http://{server_ip}:{server_port}{login2}
        $ curl -v --cookie 'session=aaaa.bb.cccc' http://{server_ip}:{server_port}

        - echo
        $ curl -v http://{server_ip}:{server_port}{echo}

        - upload
        $ curl -X POST -F "file=@/path/file" http://{server_ip}:{server_port}{upload}

        - sleep
        $ curl -v http://{server_ip}:{server_port}{sleep}

        - random with sleep
        $ curl -v http://{server_ip}:{server_port}{random}

        - dision by zero
        $ curl -v http://{server_ip}:{server_port}{crash}
        '''.format(**{
                'server_ip':        request.server[0],
                'server_port':      request.server[1],

                'login':            url_for('login'),
                'login2':           url_for('login2'),
                'upload':           url_for('upload'),
                'random':           url_for('random'),
                'sleep':            url_for('sleep'),
                'crash':            url_for('crash'),
                'echo':             url_for('echo'),
            }), _body_text)

        if 'id' in session or 'username' in session:

            username = None
            login_type = '[ client side ]'

            # login with server side
            if 'id' in session and session['id'] in _session:
                username = _session[session['id']]['username']

                login_type = '[ server side ]'

            # login with client side
            elif 'username' in session:
                username = session['username']

            else:
                return response

            response =  'Logged in as {username}. {login_type}\n'.format(**{
                    'username':   username,
                    'login_type': login_type,
            })

        return response

    # render html
    response = '''
        You are not logged in.
        <br/><a href="{login}">login, client side</a>
        <br/><a href="{login2}">login, server side</a>
        <br/><a href="{login3}">login, fake servlet server side</a>
        <br/><a href="{cookie}">inject cookie</a>
        <br/><a href="{echo}">echo</a>
        <br/><a href="{sleep}">sleep</a>
        <br/><a href="{upload}">upload</a>
        <br/><a href="{random}">random with sleep</a>
        <br/><a href="{crash}">division by zero</a>
    '''.format(**{
            'login':   url_for('login'),
            'login2':  url_for('login2'),
            'login3':  url_for('login3'),
            'cookie':  url_for('cookie'),
            'upload':  url_for('upload'),
            'random':  url_for('random'),
            'sleep':   url_for('sleep'),
            'echo':    url_for('echo'),
            'crash':   url_for('crash'),
    })

    if 'id' in session or \
            'username' in session or \
            request.cookies.get('JSESSIONID'):

        username = None
        login_type = '[ client side ]'

        _id = request.cookies.get('JSESSIONID')

        # login with server side
        if 'id' in session and session['id'] in _session:
            username = _session[session['id']]['username']

            login_type = '[ server side ]'

        elif _id and signer.loads(_id) in _session:

            username = _session[signer.loads(_id)]['username']

            login_type = '[ servlet side ]'

        # login with client side
        elif 'username' in session:
            username = session['username']

        else:
            return patch_response(response)

        response =  '''
            Logged in as {username}. {login_type}
            <br/><a href="{logout}">logout</a>
        '''.format(**{
                'username':   username,
                'login_type': login_type,
                'logout':     url_for('logout'),
        })

    return patch_response(response)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        # session [client side]
        session['username'] = request.form['username']
        return redirect(url_for('index'))

    return patch_response('''
                            <form method="post">
                                <p><input type=text name=username>
                                <p><input type=submit value=Login>
                            </form>
                            '''
    )

@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':

        _id = uuid4().hex

        # session [client side]
        session['id'] = _id

        # session [server side]
        _session[session['id']] = {}
        _session[session['id']]['username'] = request.form['username']
        return redirect(url_for('index'))

    return patch_response('''
                            <form method="post">
                                <p><input type=text name=username>
                                <p><input type=submit value=Login>
                            </form>
                            '''
    )

# fake java servlet
@app.route('/login3', methods=['GET', 'POST'])
def login3():
    if request.method == 'POST':

        response = make_response(redirect(url_for('index')))

        _id = uuid4().hex

        # session [client side]
        response.set_cookie('JSESSIONID', signer.dumps(_id))

        # session [server side]
        _session[_id] = {}
        _session[_id]['username'] = request.form['username']

        return response

    return patch_response('''
                            <form method="post">
                                <p><input type=text name=username>
                                <p><input type=submit value=Login>
                            </form>
                            '''
    )

@app.route('/logout')
def logout():

    # logout server side
    if 'id' in session:

        if session['id'] in _session:
            del _session[session['id']]

        session.pop('id')

    # logout client side
    session.pop('username', None)

    response = make_response(redirect(url_for('index')))

    # logout servlet
    _id = request.cookies.get('JSESSIONID')

    if _id:
        response.delete_cookie('JSESSIONID')

        if signer.loads(_id) in _session:
            del _session[signer.loads(_id)]

    return response


@app.route('/cookie')
def cookie():
    response =  patch_response('''
            injected cookie.
            <br/><a href="{index}">index</a>
        '''.format(**{'index': url_for('index')}),
    )

    response.set_cookie('LookAtMe', 'I see you.')

    return response

@app.route('/crash')
def crash():
    1/0

@app.route('/sleep')
def sleep():
    time.sleep(60)

    # default text
    if request.accept_mimetypes['*/*'] == 1:
        return patch_response('''
        Sorry, i think i fell asleep.
        ''', _body_text)

    return patch_response('''
            Sorry, i think i fell asleep.
            <br/><a href="{index}">index</a>
        '''.format(**{'index': url_for('index')}),
    )

@app.route('/random')
def random():
    time.sleep(30)

    # default text
    if request.accept_mimetypes['*/*'] == 1:
        return patch_response('''
        uuid: {uuid}
        '''.format(**{'uuid': uuid4()}), _body_text)

    return patch_response('''
            uuid: {uuid}
            <br/><a href="{index}">index</a>
        '''.format(**{'index': url_for('index'), 'uuid': uuid4()}),
    )

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        filename = "null"
        size = 0
        if 'file' in request.files:
            filename = request.files['file'].filename
            size     = request.content_length
        return patch_response(f'filename: {filename} size: {size}')

    html = '''
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

    return patch_response(html)


@app.route('/echo', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def echo():
    headers = request.headers
    cookies = request.cookies

    if request.accept_mimetypes['*/*'] == 1:
        text = '\n\rheaders:\n\r'
        for k, v in headers.items():
            text = f'{text}    {k}: {v}\n\r'

        text = f'{text}cookies:\n\r'
        for k, v in cookies.items():
            text = f'{text}    {k}: {v}\n\r'
        text = f'{text}'

        return patch_response(text, _body_text)

    html = '<pre>--headers:<br/>'
    for k, v in headers.items():
        html = f'{html}\t<b>{k}</b>: {v}<br/>'

    html = f'{html}--cookies:<br/>'
    for k, v in cookies.items():
        html = f'{html}\t<b>{k}</b>: {v}<br/>'
    html = f'{html}</pre>'

    return patch_response(html)

