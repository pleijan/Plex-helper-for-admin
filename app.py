import os

import requests
from flask import Flask, render_template, request, url_for, redirect,session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'clesecretedefou'
Base = declarative_base()

global connecteduser # variable globale pour savoir si un utilisateur est connecté
connecteduser = None

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    Title = Column(String, nullable=False)
    Year = Column(String)
    imdbID = Column(String)
    Poster = Column(String)


# Connexion à la première base de données
user = create_engine('sqlite:///bdd.db')
Base.metadata.create_all(user)
SessionUser = sessionmaker(bind=user)
sessionUser = SessionUser()


def user_to_dict(user):
    return {'id': user.id, 'name': user.name, 'password': user.password, 'email': user.email}


@app.route('/')
def index():
    connecteduser = session.get('connecteduser', None)
    return render_template('index.html', connecteduser=connecteduser)


@app.route('/user')
def user():
    connecteduser = session.get('connecteduser', None)
    if connecteduser:
        return render_template('user.html', connecteduser=connecteduser)
    else:
        return redirect(url_for('connexion_inscription'))

@app.route('/connexion_inscription')
def connexion_inscription():
    connecteduser = session.get('connecteduser', None)
    if connecteduser:
        return redirect(url_for('user'))
    else:
        alert = request.args.get('alert', None)
        if alert:
            return render_template('connexion_inscription.html', alert=alert)
        else:
            return render_template('connexion_inscription.html')

@app.route('/connexion', methods=['POST'])
def connexion():
    connecteduser = session.get('connecteduser', None)
    if connecteduser:
        return redirect(url_for('user'))
    else:
        if request.method == 'POST':
            # verify if the user is in the database
            username = request.form['username']
            password = request.form['password']
            if sessionUser.query(User).filter_by(name=username,password=password).first() != None:
                user = sessionUser.query(User).filter_by(name=username,password=password).first()
                session['connecteduser'] = user_to_dict(user)
                return redirect(url_for('user'))
            else:
                alert = "Mauvais identifiants"
                return redirect(url_for('connexion_inscription', alert=alert))

@app.route('/deconnexion')
def deconnexion():
    session.pop('connecteduser', None)
    return redirect(url_for('index'))


@app.route('/inscription', methods=['POST'])
def inscription():
    connecteduser = session.get('connecteduser', None)
    if connecteduser:
        return redirect(url_for('user'))
    else:
        if request.method == 'POST':
            # add user to database
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # Assuming your SQLAlchemy model class is named 'User'
            new_user = User(name=username, password=password, email=email)

            sessionUser.add(new_user)
            sessionUser.commit()

            session['connecteduser'] = user_to_dict(new_user)

            return redirect(url_for('user'))
        else:
            alert = "Mauvais identifiants"
            return redirect(url_for('connexion_inscription', alert=alert))


@app.route('/film/<imdbid>')
def film(imdbid):
    connecteduser = session.get('connecteduser', None)
    # ask api for information about the film and return a json
    payload = { 'i': imdbid,'apikey': 'ffc487eb', 'plot': 'full'}
    r = requests.get('https://www.omdbapi.com/', params=payload)
    print(r.json())
    return render_template('film.html', movie=r.json(), connecteduser=connecteduser)


@app.route('/recherche', methods=['GET', 'POST'])
def search():

    connecteduser = session.get('connecteduser', None)

    if request.method == 'GET':
        # ask API for movies that return a json to store on a variable

        payload = { 's': request.args.get('movie', ''),'apikey': 'ffc487eb'}
        r = requests.get('https://www.omdbapi.com/', params=payload)
        print (r.json())
        if r.json()['Response'] == 'False':
            alert = "Aucun film ne correspond à votre recherche"
            return render_template('index.html', alert=alert, connecteduser=connecteduser)

        return render_template('index.html', movies=r.json()['Search'], connecteduser=connecteduser)

    elif request.method == 'POST':
        # get the value of the input with name 'movie' and add it to database
        movie = request.form['movie']
        # add movie to database
        new_movie = Movie(Title=movie)
        sessionMovie.add(new_movie)
        sessionMovie.commit()
        return redirect(url_for('index'))

@app.route('/ajout/<IDimdb>')
def ajout(IDimdb):
    connecteduser = session.get('connecteduser', None)
    payload = { 'i': IDimdb,'apikey': 'ffc487eb'}
    r = requests.get('https://www.omdbapi.com/', params=payload)
    print(r.json())
    new_movie = Movie(Title=r.json()['Title'], Year=r.json()['Year'], imdbID=r.json()['imdbID'], Poster=r.json()['Poster'])
    sessionMovie.add(new_movie)
    sessionMovie.commit()
    alert = "Le film a bien été ajouté"
    return render_template('index.html', alert=alert, connecteduser=connecteduser)

@app.route('/to_download')
def to_download():
    connecteduser = session.get('connecteduser', None)
    #si l'utilisateur est admin, on affiche tous les films
    if connecteduser != None and connecteduser['name'] == 'admin':
        movies = sessionMovie.query(Movie).all()
        return render_template('a_telecharger.html', added_movies=movies, connecteduser=connecteduser)
    #sinon retour à l'accueil
    else:
        return redirect(url_for('index'))


@app.route('/delete/<imdbid>')
def delete(imdbid):

    movie = sessionMovie.query(Movie).filter_by(imdbID=imdbid).first()
    sessionMovie.delete(movie)
    sessionMovie.commit()
    return redirect(url_for('to_download'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
