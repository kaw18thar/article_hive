from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Collection, ArticleCollection, Comments


app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=false')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# the main page of the app. Lists all the collections


@app.route('/')
@app.route('/collections/')
def DefaultCollections():
    return ("This is the default route of all collections")


# viewing a collection of articles

@app.route('/collections/<int:collection_id>/')
@app.route('/collections/<int:collection_id>/list/')
def collectionList(collection_id):
    return ("Articles of  collection no {collection}").format(
        collection=collection_id)

# creating new collection


@app.route('/collections/new')
def newCollection():
    return ("PAge for creating new collection")


# editing the name of a collection

@app.route('/collections/<int:collection_id>/edit')
def editCollection(collection_id):
    return ("edit collection no {collection}").format(collection=collection_id)

# deleting a collection


@app.route('/collections/<int:collection_id>/delete')
def deleteCollection(collection_id):
    return ('delete collection  {collection}').format(collection=collection_id)

# adding new article to collecton no collection_id


@app.route('/collections/<int:collection_id>/new')
def newArticle(collection_id):
    return ("new article in collection {collection}").format(
        collection=collection_id)

# editing an article


@app.route('/collections/<int:collection_id>/<int:article_id>/edit')
def editArticle(collection_id, article_id):
    return ("edit article {article} in collection {collection}").format(
        article=article_id, collection=collection_id)

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
