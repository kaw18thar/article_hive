from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from flask import session as login_session
import random, string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Collection, ArticleCollection, Comments


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Article Hive Collections"

engine = create_engine(
    'sqlite:///collectionsarticles.db?check_same_thread=false')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# the main page of the app. Lists all the collections

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output



@app.route('/')
@app.route('/collections/')
def DefaultCollections():
    collections = session.query(Collection).group_by(Collection.id).all()
    return render_template('collections.html', collections=collections)


# viewing a collection of articles

@app.route('/collections/<int:collection_id>/')
@app.route('/collections/<int:collection_id>/list/')
def collectionList(collection_id):
    collection = session.query(Collection).filter_by(
        id=collection_id).one()
    articles = session.query(ArticleCollection).filter_by(
        collection_id=collection_id)
    return render_template(
        'collectionList.html',
        collection=collection,
        articles=articles)

# creating new collection


@app.route('/collections/new', methods=['GET', 'POST'])
def newCollection():
    if request.method == 'POST':
        newi = Collection(name=request.form['name'])
        session.add(newi)
        session.commit()
        flash("new collection created!")
        return redirect(url_for('DefaultCollections'))
    else:
        return render_template('newcollection.html')


# editing the name of a collection

@app.route('/collections/<int:collection_id>/edit', methods=['GET', 'POST'])
def editCollection(collection_id):
    itemToedit = session.query(Collection).filter_by(id=collection_id).one()
    if request.method == 'POST':
        itemToedit.name = request.form['name']
        session.add(itemToedit)
        session.commit()
        flash("collection name edited!")
        return redirect(url_for('DefaultCollections'))
    else:
        return render_template(
            'editcollection.html',
            collection_id=collection_id,
            coll=itemToedit)

# deleting a collection


@app.route('/collections/<int:collection_id>/delete', methods=['GET', 'POST'])
def deleteCollection(collection_id):
    itemTodelete = session.query(Collection).filter_by(id=collection_id).one()
    if request.method == 'POST':
        session.delete(itemTodelete)
        session.commit()
        flash("collection deleted!")
        return redirect(url_for('DefaultCollections'))
    else:
        return render_template(
            'deletecollection.html',
            collection_id=collection_id,
            coll=itemTodelete)

# adding new article to collecton no collection_id


@app.route('/collections/JSON')
def collectionsJSON():
    collections = session.query(Collection).group_by(Collection.id).all()
    return jsonify(Collecions=[i.serialize for i in collections])


@app.route('/collections/<int:collection_id>/new', methods=['GET', 'POST'])
def newArticle(collection_id):
    if request.method == 'POST':
        newarticle = ArticleCollection(name=request.form['name'],
                                       description=request.form['description'],
                                       text=request.form['text'],
                                       collection_id=collection_id)
        session.add(newarticle)
        session.commit()
        flash("new article added!")
        return redirect(
            url_for(
                'viewArticle',
                collection_id=collection_id,
                article_id=newarticle.id))
    else:
        return render_template("newarticle.html", collection_id=collection_id)

# editing an article


@app.route(
    '/collections/<int:collection_id>/<int:article_id>/edit',
    methods=[
        'GET',
        'POST'])
def editArticle(collection_id, article_id):
    itemToedit = session.query(
        ArticleCollection).filter_by(id=article_id).one()
    if request.method == 'POST':
        itemToedit.name = request.form['name']
        itemToedit.description = request.form['description']
        itemToedit.text = request.form['text']
        session.add(itemToedit)
        session.commit()
        flash("article edited!")
        return redirect(
            url_for(
                'viewArticle',
                collection_id=collection_id,
                article_id=article_id))

    else:
        return render_template('editarticle.html',
                               collection_id=collection_id,
                               article_id=article_id, art=itemToedit)

# deleting an article


@app.route(
    '/collections/<int:collection_id>/<int:article_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteArticle(collection_id, article_id):
    itemTodelete = session.query(
        ArticleCollection).filter_by(id=article_id).one()
    if request.method == 'POST':
        session.delete(itemTodelete)
        session.commit()
        flash("article deleted!")
        return redirect(url_for('collectionList', collection_id=collection_id))
    else:
        return render_template(
            'deletearticle.html',
            collection_id=collection_id,
            article_id=article_id,
            art=itemTodelete)

# viewing an article


@app.route(
    '/collections/<int:collection_id>/<int:article_id>/',
    methods=[
        'GET',
        'POST'])
@app.route(
    '/collections/<int:collection_id>/<int:article_id>/view',
    methods=[
        'GET',
        'POST'])
def viewArticle(collection_id, article_id):
    item = session.query(ArticleCollection).filter_by(id=article_id).one()
    collection = session.query(Collection).filter_by(id=collection_id).one()
    if request.method == 'POST':
        session.delete(itemTodelete)
        session.commit()
        flash("article deleted!")
        return redirect(url_for('collectionList', collection_id=collection_id))
    else:
        return render_template(
            'viewarticle.html',
            collection_id=collection_id,
            coll=collection,
            article_id=article_id,
            art=item)


@app.route('/collections/<int:collection_id>/JSON')
def collectionsArticleJSON(collection_id):
    collections = session.query(Collection).filter_by(id=collection_id).one()
    arts = session.query(ArticleCollection).filter_by(
        collection_id=collection_id)
    return jsonify(Articles=[i.serialize for i in arts])


@app.route('/collections/<int:collection_id>/<int:article_id>/JSON')
def ArticleJSON(collection_id, article_id):
    art = session.query(ArticleCollection).filter_by(id=article_id).one()
    return jsonify(Article=art.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
