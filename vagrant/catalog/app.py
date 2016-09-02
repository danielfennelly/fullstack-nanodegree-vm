from flask import Flask, flash, jsonify, redirect, render_template, \
    request, url_for
from flask import session as login_session
from utils import json_response, token, login_required, request_wants_json

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apiclient.discovery import build
import httplib2
from oauth2client import client

from database_setup import Base, User, Category, Item

app = Flask(__name__)
app.secret_key = token()

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_SECRET_FILE = 'client_secrets.json'
with open('client_secrets.json', 'r') as client_secrets:
    CLIENT_ID = json.loads(client_secrets.read())['web']['client_id']


def createUser(google_id, name, email, picture_url):
    newUser = User(google_id=google_id, name=name, email=email,
                   picture_url=picture_url)
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(google_id=google_id).one()
    return user


def getUserByGoogleId(google_id):
    try:
        user = session.query(User).filter_by(google_id=google_id).one()
        return user
    except:
        return None


def getUser():
    google_id = login_session.get('google_id')
    if google_id:
        return getUserByGoogleId(google_id)
    return None


def getCategories():
    return session.query(Category).all()


def getCategory(category_name):
    return session.query(Category).\
        filter(Category.name == category_name).\
        one()


def findCategory(category_name, categories):
    for category in categories:
        if category.name == category_name:
            return category
    return None


def getItems():
    return session.query(Item).all()


def getItemsByCategory(category_name):
    return session.query(Item).join(Category).\
        filter(Category.name == category_name).\
        all()


def getItemByName(item_name):
    return session.query(Item).filter(Item.name == item_name).one()


def getItemAndCategory(category_name, item_name):
    return session.query(Item, Category).\
        filter(Item.name == item_name).\
        filter(Category.name == category_name).\
        one()


def findItem(item_name, items):
    for item in items:
        if item.name == item_name:
            return item
    return None


# -----------------
# Routing Functions
# -----------------


@app.route('/')
def index():
    user = getUser()
    categories = getCategories()
    items = getItems()

    if request_wants_json():
        index_data = {
            'categories': [category.serialize for category in categories],
            'recent_items': [item.serialize for item in items]}
        return jsonify(index_data)

    return render_template('index.html', categories=categories, items=items,
                           user=user)

# ------------------------
# Authentication Endpoints
# ------------------------


@app.route('/gconnect', methods=['POST'])
def gconnect():
    state_token = request.args.get('state')
    if state_token != login_session['state']:
        return json_response('Invalid State Parameter', 401)
    auth_code = request.data
    print('auth_code %s' % str(auth_code))

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['profile', 'email'],
        auth_code)

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    google_id = credentials.id_token['sub']
    login_session['google_id'] = google_id

    # Call Google API
    http = credentials.authorize(httplib2.Http())
    service = build('plus', 'v1', http=http)
    people_resource = service.people()
    people_document = people_resource.get(userId='me').execute()

    # Get profile info from ID token
    name = people_document['displayName']
    email = credentials.id_token['email']
    picture_url = people_document['image']['url']

    # Get the user
    user = getUserByGoogleId(login_session['google_id'])

    # Create the user if they don't exist in our system yet
    if not user:
        user = createUser(google_id, name, email, picture_url)

    # Load their data into the session
    login_session['username'] = name
    login_session['email'] = email
    login_session['picture'] = picture_url

    flash('Logged in as %s' % name)
    return redirect('/')


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    credentials = client.OAuth2Credentials.from_json(
        login_session.get('credentials'))
    if credentials is None:
        return json_response('Current user not connected', 401)
    else:
        access_token = credentials.access_token
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
            access_token
        http = httplib2.Http()
        result = http.request(url, 'GET')[0]

        if result['status'] == '200':
            # Reset the user's session.
            del login_session['credentials']
            del login_session['google_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']

            return json_response('Successfully disconnected.')
        else:
            return json_response('Failed to revoke token.', 400)


@app.route('/login')
def login():
    user = getUser()
    if user:
        return redirect('/')
    login_session['state'] = token()
    return render_template('login.html', STATE=login_session['state'])

# ------------------
# Category Endpoints
# ------------------


@app.route('/category/<string:category_name>')
def category(category_name):
    user = getUser()
    categories = getCategories()
    category = findCategory(category_name, categories)

    if category:
        items = getItemsByCategory(category_name)

        if request_wants_json():
            category_dict = category.serialize
            category_dict['items'] = [item.serialize for item in items]
            return jsonify(category_dict)
        return render_template('index.html', category=category,
                               items=items, categories=categories, user=user)
    else:
        return json_response('Category not found', 404)


@app.route('/new_category', methods=['GET', 'POST'])
@login_required
def new_category():
    user = getUser()
    if request.method == 'GET':
        return render_template('edit_category.html', user=user)
    else:
        name = request.form['category-name']
        description = request.form['category-description']

        existing_category = getCategory(name)
        if existing_category:
            return json_response('Category with that name already exists', 400)

        category = Category(name=name, description=description, user=user)
        session.add(category)
        session.commit()
        flash('Created category %s' % category.name)
        return redirect('/')


@app.route('/category/<string:category_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_name):
    user = getUser()
    category = getCategory(category_name)
    if not category:
        return json_response('Category not found', 404)
    if category.user is not user:
        return json_response('Editing category forbidden', 403)
    if request.method == 'GET':
        return render_template('edit_category.html', category=category,
                               user=user)
    else:
        name = request.form['category-name']
        description = request.form['category-description']
        category.name = name
        category.description = description
        session.commit()
        flash('Successfully modified %s' % category.name)
        return redirect(url_for('category', category_name=category_name))


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
@login_required
def delete_category(category_name):
    user = getUser()
    category = getCategory(category_name)

    if not category:
        return json_response('Category not found', 404)

    if category.user is not user:
        return json_response('Deleting category forbidden', 403)

    items = getItemsByCategory(category_name)
    if items:
        return json_response('Cannot delete category with items in it.', 400)

    if request.method == 'GET':
        return render_template(
            'delete_entity.html',
            entity=category,
            path=url_for('delete_category', category_name=category_name),
            user=user)
    else:
        session.delete(category)
        session.commit()
        flash('Successfully deleted %s' % category.name)
        return redirect('/')


# --------------
# Item Endpoints
# --------------

@app.route('/category/<string:category_name>/item/<string:item_name>')
def item(category_name, item_name):
    user = getUser()
    category_items = getItemsByCategory(category_name)
    category = getCategory(category_name)
    item = findItem(item_name, category_items)
    if item:
        if request_wants_json():
            return jsonify(item.serialize)
        return render_template('item.html', item=item, items=category_items,
                               category=category, user=user)
    else:
        return json_response('Item not found', 404)


@app.route('/category/<string:category_name>/new_item',
           methods=['GET', 'POST'])
@login_required
def new_item(category_name):
    user = getUser()
    if request.method == 'GET':
        categories = getCategories()
        category = findCategory(category_name)
        return render_template('edit_item.html', category=category,
                               categories=categories, user=user)
    else:
        name = request.form['item-name']
        description = request.form['item-description']
        category_name = request.form['category']

        category = getCategory(category_name)
        if not category:
            return json_response('Category not found.', 404)

        existing_item = getItemByName(name)
        if existing_item:
            return json_response('Item with that name already exists.', 400)

        item = Item(name=name,
                    description=description,
                    category=category,
                    user=user)
        session.add(item)
        session.commit()
        flash('Created item %s' % item.name)
        return redirect('/category/%s' % category.name)


@app.route('/category/<string:category_name>/item/<string:item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def edit_item(category_name, item_name):
    user = getUser()
    item, category = getItemAndCategory(category_name, item_name)
    if category.user is not user:
        return json_response('Editing item forbidden', 403)

    categories = getCategories()
    if request.method == 'GET':
        return render_template('edit_item.html',
                               categories=categories,
                               category=category,
                               item=item,
                               user=user)
    else:
        name = request.form['item-name']
        description = request.form['item-description']
        new_category_name = request.form['category']

        new_category = getCategory(new_category_name)
        if not new_category:
            return json_response('Category not found.', 404)

        item.name = name
        item.description = description
        item.category = new_category
        session.commit()
        flash('Successfully modified %s' % item.name)
        return redirect(url_for('item', category_name=category.name,
                        item_name=item.name))


@app.route('/category/<string:category_name>/item/<string:item_name>/delete',
           methods=['GET', 'POST'])
@login_required
def delete_item(category_name, item_name):
    user = getUser()
    item, _ = getItemAndCategory(category_name, item_name)
    if item.user is not user:
        return json_response('Deleting item forbidden', 403)
    if item:
        session.delete(item)
        session.commit()
        flash('Deleted item %s' % item_name)
        return redirect('/')
    else:
        return json_response('Item not found', 404)

# --------------
# Main
# --------------

if __name__ == '__main__':
    app.run(host='0.0.0.0')
