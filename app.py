#
# Vinicio Valubena
#
# python3 -m venv env
# source env/bin/activate
# pip install -r requirements.txt
# FLASK_ENV=development flask run --debugger
#

import socket
import time

from flask import Flask
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import make_response

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
# python -c 'import os; print(os.urandom(16))'
app.secret_key = b'[SECRET_KEY_HERE]'

_body = '''
    <br/>
    <pre>
        hostname: {hostname}
        server:   {server_ip}:{server_port}
        client:   {client_ip}:{client_port}
    </pre>
    {response}
'''

@app.route('/')
def index():
    _response = '''
        You are not logged in.
        <br/><a href="{login}">login</a>
        <br/><a href="{cookie}">inject cookie</a>
        <br/><a href="{sleep}">sleep</a>
        <br/><a href="{crash}">division by zero</a>
    '''.format(**{
            'login':  url_for('login'),
            'cookie': url_for('cookie'),
            'sleep':  url_for('sleep'),
            'crash':  url_for('crash'),
    })

    if 'username' in session:
        _response =  '''
            Logged in as {username}.
            <br/><a href="{logout}">logout</a>
        '''.format(**{
                'username': session['username'],
                'logout':     url_for('logout'),
        })

    response = make_response(_body.format(**{
        'hostname':                    socket.gethostname(),
        'server_ip':                   request.server[0],
        'server_port':                 request.server[1],
        'client_ip':      request.environ['REMOTE_ADDR'],
        'client_port':    request.environ['REMOTE_PORT'],
        'response':                            _response,
    }))

    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))

    response =  make_response(_body.format(**{
        'hostname':                    socket.gethostname(),
        'server_ip':                   request.server[0],
        'server_port':                 request.server[1],
        'client_ip':      request.environ['REMOTE_ADDR'],
        'client_port':    request.environ['REMOTE_PORT'],
        'response':        '''
                            <form method="post">
                                <p><input type=text name=username>
                                <p><input type=submit value=Login>
                            </form>
                            '''
        }))

    return response

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/cookie')
def cookie():
    response =  make_response(_body.format(**{
        'hostname':                    socket.gethostname(),
        'server_ip':                   request.server[0],
        'server_port':                 request.server[1],
        'client_ip':      request.environ['REMOTE_ADDR'],
        'client_port':    request.environ['REMOTE_PORT'],
        'response':       '''
            injected cookie.
            <br/><a href="{index}">index</a>
        '''.format(**{'index': url_for('index')}),
    }))

    response.set_cookie('LookAtMe', 'I see you.')

    return response

@app.route('/crash')
def crash():
    1/0

@app.route('/sleep')
def sleep():
    time.sleep(60)

    response =  make_response(_body.format(**{
        'hostname':                    socket.gethostname(),
        'server_ip':                   request.server[0],
        'server_port':                 request.server[1],
        'client_ip':      request.environ['REMOTE_ADDR'],
        'client_port':    request.environ['REMOTE_PORT'],
        'response':       '''
            Sorry, i think i fell asleep.
            <br/><a href="{index}">index</a>
        '''.format(**{'index': url_for('index')}),
    }))

    return response
