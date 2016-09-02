import json
import random
import string
from flask import make_response, session, request, redirect, url_for
from functools import wraps


def token(n=32):
    chars = random.sample(string.ascii_uppercase + string.digits, n)
    return ''.join(chars)


def json_response(message, status_code=200):
    response = make_response(json.dumps(message), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


# From the Flask docs
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('google_id') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# From the Flask snippets
def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']
