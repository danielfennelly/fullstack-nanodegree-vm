import flask
from utils import json_response, token

app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    return flask.render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'  # TODO: Change this
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
