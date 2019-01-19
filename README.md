# article_hive
This repository is for full stack nanodegree item catalog project

## Objective
Article Hive is a website that allows users to create collections of articles and comment on each other's articles. The user can sign up using google plus (and soon Facebook and Stack Exchange too)

## How To Start?
1- Download Git Bash or simply use your terminal program on MacOS or Linux
2- Download the latest version of vagrant
3- Download the latest version of virtualBox
4- Clone this repository
5- in Git Bash or your terminal, run `vagrant up` then `vagrant ssh` 
6- Cd `cd /vagrant ` then `cd article_hive`
7- Run `Python database_setup.py` to set up our database. This will create a database file `collectionsarticlesusers` and a `database_setup.pyc` file. These files must not be edited. The only changes you will have to make need to be made in the original ` database_setup.py` file. Though, please notice that altering of columns could make the app to display an error, in this case, delete the .db file, do whatever changes you would like to make to the database_setup.py and then run `Python database_setup.py` to create a new and improved database.
8- Run the `python createcollections.py` to create 2 collections and 4 articles
9- Run `python finalProject.py` to start the application
10- Go to http://localhost:5080 in your browser to browse collections and articles.

## Files
- client_secrets.json 
    contains our client secret used to authenticate log ins via google plus
- `collectionsarticlesusers.db`
    should be created after the run of step number 7 and should not be deleted or tampered with in order for our app to run properly.           Unless after updating the database_setup file
- `database_setup.py`
    the file containing our database classes and database setup using sqlalchemy
- `createcollections.py`
    the file that we will use to create some data to run our app. Though not neccessary for our app to function. You can just run the           database_setup.py and the `finalProject.py` and the app will run just fine
- `newcreatecollections.py`
    when run with python, it will genereate some dummy comments. Runing this file too is unnecessary for an error-free runing of Article-       Hive app.
    - README.MD
    this file
    - .gitignore
    - `templates` folder
    contains the html pages
    `static` folder 
    cotains the css file and bacground images for our app
   
  ## Logging in and signing up
  
  click on the `log in or sign up` link on each page, this will take you to the login/signaup page that will contain a google sign in button, upon clickin on this button the user will be taken to a google page that will ask his permission to allow Article Hive app to use his info. Clicking on the profile picture is what it takes to do so, if the user do agree to use Article Hive. This will register the user as a new Article Hive user if he is loggin in for the first time.
  
  ## JSON links for API Access
localhost:5080/collections/JSON
will list all the collections and its articles and owner
localhost:5080/collections/<int:collection_id>/JSON
will list article of collection with id = collection_id
localhost:5080/collections/<int:collection_id>/<int:article_id>/JSON
will list the single article with id = article_id

## helpful resources 
Udacity full-stack web developer nanodegree for the gconnect and gdisconnect methods.
## background photo courtsey of Holman Galeano at Toptal:
https://www.toptal.com/designers/subtlepatterns/full-bloom-pattern/
