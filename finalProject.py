from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Collection, ArticleCollection, Comments


app = Flask(__name__)

engine = create_engine('sqlite:///collectionsarticles.db?check_same_thread=false')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# the main page of the app. Lists all the collections


@app.route('/')
@app.route('/collections/')
def DefaultCollections():
    collections = session.query(Collection).group_by(Collection.name).all()
    return render_template('collections.html', collections=collections)


# viewing a collection of articles

@app.route('/collections/<int:collection_id>/')
@app.route('/collections/<int:collection_id>/list/')
def collectionList(collection_id):
    collection = session.query(Collection).filter_by(
                                                     id
                                                     =collection_id).one()
    articles = session.query(ArticleCollection).filter_by(
                                              collection_id=
                                              collection_id)
    return render_template('collectionList.html', collection=collection, articles=articles)

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
        return render_template('editcollection.html', collection_id=collection_id, coll=itemToedit)

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
        return render_template('deletecollection.html', collection_id=collection_id, coll=itemTodelete)

# adding new article to collecton no collection_id


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
        return redirect(url_for('collectionList', collection_id=collection_id))
    else:
        return render_template("newarticle.html", collection_id=collection_id)

# editing an article


@app.route('/collections/<int:collection_id>/<int:article_id>/edit', methods=['GET', 'POST'])
def editArticle(collection_id, article_id):
    itemToedit = session.query(ArticleCollection).filter_by(id=article_id).one()
    if request.method == 'POST':
        itemToedit.name = request.form['name']
        itemToedit.description = request.form['description']
        itemToedit.text = request.form['text']
        session.add(itemToedit)
        session.commit()
        flash("item edited!")
        return redirect(url_for('collectionList', collection_id=collection_id))

    else:
        return render_template('editarticle.html',
                               collection_id=collection_id,
                               article_id=article_id, art=itemToedit)

# deleting an article


@app.route('/collections/<int:collection_id>/<int:article_id>/delete')
def deleteArticle(collection_id, article_id):
    return ("delete article {article} in collection {collection}").format(
        article=article_id, collection=collection_id)

# viewing an article


@app.route('/collections/<int:collection_id>/<int:article_id>/')
@app.route('/collections/<int:collection_id>/<int:article_id>/view')
def viewArticle(collection_id, article_id):
    return ("view article {article} in collection {collection}").format(
        article=article_id, collection=collection_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
