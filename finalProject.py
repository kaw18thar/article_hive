from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from flask import session as login_session
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Collection, ArticleCollection, Comments, User


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
    'sqlite:///collectionsarticlesusers.db?check_same_thread=false')
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
    print "gplus id object" + gplus_id
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
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    print "data of the login req: ", data
    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])

    print "user id before creationof user is" + "email is: " + login_session['email']
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['name']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['name'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['name']
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
        login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['name']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully disconnected.")
        return redirect(url_for('DefaultCollections'))
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/collections/')
def DefaultCollections():

    if 'name' not in login_session:
        c = session.query(
            Collection.name.label('cname'),
            User.name.label('uname'),
            Collection.id.label('cid'),
            User.id.label('uid')).join(
            User,
            User.id == Collection.user_id).add_columns(
            User.id,
            User.name,
            Collection.name,
            Collection.id).all()
        return render_template('publicCollections.html', c=c)
    else:
        loggedinuser = login_session['user_id']
        collecInfo = session.query(
            Collection.name.label('cname'),
            User.name.label('uname'),
            Collection.id.label('cid'),
            User.id.label('uid')).join(
            User).add_columns(
            User.id,
            User.name,
            Collection.name,
            Collection.id).all()
        print "Collection id, name, user id: ", collecInfo
        return render_template(
            'collections.html',
            loggedinuser=loggedinuser,
            collecInfo=collecInfo)


@app.route('/<int:user_id>/')
def viewAuthor(user_id):
    if 'name' not in login_session:
        flash('unauthorized to view authors collections')
        return redirect(url_for('DefaultCollections'))
    else:
        collections = session.query(Collection).filter_by(user_id=user_id)
        author = getUserInfo(user_id)
        return render_template(
            'author.html',
            collections=collections,
            author=author)


# viewing a collection of articles

@app.route('/collections/<int:collection_id>/')
@app.route('/collections/<int:collection_id>/list/')
def collectionList(collection_id):
    if 'name' not in login_session:
        collection = session.query(Collection).filter_by(
            id=collection_id).one()
        articles = session.query(ArticleCollection).filter_by(
            collection_id=collection_id)
        return render_template(
            'publiclist.html', articles=articles, collection=collection)
    collection = session.query(Collection).filter_by(
        id=collection_id).one()
    articles = session.query(ArticleCollection).filter_by(
        collection_id=collection_id)

    artInfo = session.query(
        ArticleCollection.name.label('aname'),
        User.name.label('uname'),
        ArticleCollection.date.label('date'),
        ArticleCollection.id.label('aid'),
        User.id.label('uid')).join(
        User,
        User.id == ArticleCollection.user_id).add_columns(
            User.id,
            User.name,
            ArticleCollection.name,
        ArticleCollection.id).all()
    owner = getUserInfo(collection.user_id)
    return render_template(
        'collectionList.html',
        collection=collection,
        articles=articles, owner=owner)

# creating new collection


@app.route('/collections/new', methods=['GET', 'POST'])
def newCollection():
    if 'name' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        print "login session id:", login_session['user_id']
        newi = Collection(
            user_id=login_session['user_id'],
            name=request.form['name'])  # user_id=login_session['user_id'] ,
        session.add(newi)
        session.commit()
        flash("new collection created!")
        return redirect(url_for('DefaultCollections'))
    else:
        return render_template('newcollection.html')


# editing the name of a collection

@app.route('/collections/<int:collection_id>/edit', methods=['GET', 'POST'])
def editCollection(collection_id):
    if 'name' not in login_session:
        return redirect('/login')
    itemToedit = session.query(Collection).filter_by(id=collection_id).one()
    owner = itemToedit.user_id
    if owner == login_session['user_id']:
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
    else:
        flash("unauthorized to edit this collection")
        return redirect(url_for('DefaultCollections'))


# deleting a collection


@app.route('/collections/<int:collection_id>/delete', methods=['GET', 'POST'])
def deleteCollection(collection_id):
    if 'name' not in login_session:
        return redirect('/login')
    itemTodelete = session.query(Collection).filter_by(id=collection_id).one()
    articlesofCollection = session.query(
        ArticleCollection).filter_by(collection_id=collection_id)
    owner = itemTodelete.user_id
    if owner == login_session['user_id']:
        if request.method == 'POST':
            for a in articlesofCollection:
                session.delete(a)
                session.commit()
            session.delete(itemTodelete)
            session.commit()
            flash("collection deleted!")
            return redirect(url_for('DefaultCollections'))
        else:
            return render_template(
                'deletecollection.html',
                collection_id=collection_id,
                coll=itemTodelete)
    else:
        flash("unauthorized to delete this collection")
        return redirect(url_for('DefaultCollections'))

# adding new article to collecton no collection_id


@app.route('/collections/JSON')
def collectionsJSON():
    collections = session.query(Collection).group_by(Collection.id).all()
    return jsonify(Collecions=[i.serialize for i in collections])


@app.route('/collections/<int:collection_id>/new', methods=['GET', 'POST'])
def newArticle(collection_id):
    if 'name' not in login_session:
        return redirect('/login')
    collec = session.query(Collection).filter_by(id=collection_id).one()
    owner = collec.user_id
    if owner == login_session['user_id']:
        if request.method == 'POST':
            newarticle = ArticleCollection(
                name=request.form['name'],
                description=request.form['description'],
                text=request.form['text'],
                collection_id=collection_id,
                user_id=login_session['user_id'])  # user_id=login_session['user_id'] ,
            session.add(newarticle)
            session.commit()
            flash("new article added!")
            return redirect(
                url_for(
                    'viewArticle',
                    collection_id=collection_id,
                    article_id=newarticle.id))
        else:
            return render_template(
                "newarticle.html",
                collection_id=collection_id)
    else:
        flash("unauthorized to add to this collection")
        return redirect(url_for('collectionList', collection_id=collection_id))

# editing an article


@app.route(
    '/collections/<int:collection_id>/<int:article_id>/edit',
    methods=[
        'GET',
        'POST'])
def editArticle(collection_id, article_id):
    if 'name' not in login_session:
        return redirect('/login')
    itemToedit = session.query(
        ArticleCollection).filter_by(id=article_id).one()
    owner = itemToedit.user_id
    if owner == login_session['user_id']:
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
    else:
        flash("unauthorized to edit this article")
        return redirect(
            url_for(
                'viewArticle',
                article_id=article_id,
                collection_id=collection_id))

# deleting an article


@app.route(
    '/collections/<int:collection_id>/<int:article_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteArticle(collection_id, article_id):
    item = session.query(ArticleCollection).filter_by(id=article_id).one()
    collection = session.query(Collection).filter_by(id=collection_id).one()
    loggeduser = False
    # if a user is logged safe this variable as true and send it to the public
    # view article
    if 'name' in login_session:
        loggeduser = True

    if 'name' not in login_session or item.user_id != login_session['user_id']:
        return render_template(
            'publicArticle.html',
            collection_id=collection_id,
            coll=collection,
            article_id=article_id,
            art=item, logged=loggeduser)

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
    comments = session.query(Comments).filter_by(
                article_id=article_id).all()
    comj = json.dumps(comments)
    print comj
    item = session.query(ArticleCollection).filter_by(id=article_id).one()
    collection = session.query(Collection).filter_by(id=collection_id).one()
    loggeduser = False
    # if a user is logged safe this variable as true and send it to the public
    # view article
    if 'name' in login_session:
        loggeduser = True

    if 'name' not in login_session or item.user_id != login_session['user_id']:
        return render_template(
            'publicArticle.html',
            collection_id=collection_id,
            coll=collection,
            article_id=article_id,
            art=item, logged=loggeduser)
    else:
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            flash("article deleted!")
            return redirect(
                url_for('collectionList', collection_id=collection_id))
        else:
            comments = session.query(Comments).filter_by(
                article_id=article_id).all()
            return render_template(
                'viewarticle.html',
                collection_id=collection_id,
                coll=collection,
                article_id=article_id,
                art=item, viewer=login_session['user_id'])


@app.route(
    '/collections/<int:collection_id>/<int:article_id>#comment',
    methods=[
        'GET',
        'POST'])
@app.route(
    '/collections/<int:collection_id>/<int:article_id>/view#comment',
    methods=[
        'GET',
        'POST'])
def addComment(collection_id, article_id):
    print 'hello'
    item = session.query(ArticleCollection).filter_by(id=article_id).one()

    # let's first check that no one is using the url to view or add comments:
    if 'name' not in login_session:
        flash("unauthorized")
        return redirect(url_for('viewArticle', collection_id=collection_id,
                                article_id=article_id))  # a soft redirect
    else:
        if request.method == 'POST':
            newcomment = Comments(
                title=request.form['title'],
                text=request.form['text'],
                article_id=article_id,
                user_id=login_session['user_id'])  # user_id=login_session['user_id'] ,
            session.add(newcomment)
            session.commit()
            flash("new comment added!")
            return redirect(
                url_for(
                    'addComment',
                    collection_id=collection_id,
                    article_id=article_id))
        else:
            co = session.query(
                Comments.title.label('ctitle'),
                Comments.text.label('ctext'),
                Comments.date.label('date'),
                User.name.label('owner'),
                Comments.id.label('cid'),Comments.user_id.label('cuid'),
                Comments.article_id.label('caid'),
                ArticleCollection.id.label('aid'),
                User.id.label('uid')).filter(
                ArticleCollection.id == Comments.article_id).add_columns(
                Comments.article_id,
                ArticleCollection.id,
                User.id,
                User.name,
                Comments.title,
                Comments.text,
                Comments.date,
                Comments.id).all()
            comments = session.query(Comments).filter_by(
                article_id=article_id).all()
            article = session.query(
                ArticleCollection).filter_by(id=article_id).one()
            collect = session.query(Collection).filter_by(
                id=collection_id).one()
            return render_template('comments.html', comments=co, art=article,
                                   coll=collect, collection_id=collection_id,
                                   article_id=article_id)


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


def createUser(login_session):
    print login_session['name']
    newU = User(
        name=login_session['name'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newU)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    print user
    return user


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5080)
