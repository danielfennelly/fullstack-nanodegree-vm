import json
import random
import string
from flask import make_response


def token(n=32):
    chars = random.sample(string.ascii_uppercase + string.digits, n)
    return ''.join(chars)


def json_response(message, status_code=200):
    response = make_response(json.dumps(message), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response
