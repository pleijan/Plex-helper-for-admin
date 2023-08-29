import os

import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
    db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    Year = db.Column(db.String(4))
    imdbID = db.Column(db.String(10))
    Poster = db.Column(db.String(200))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
   return render_template('index.html')


@app.route('/recherche', methods=['GET', 'POST'])
def search():

    if request.method == 'GET':
        # ask API for movies that return a json to store on a variable

        payload = { 's': request.args.get('movie', ''),'apikey': 'ffc487eb'}
        r = requests.get('https://www.omdbapi.com/', params=payload)
        if r.json()['Response'] == 'False':
            alert = "Aucun film ne correspond à votre recherche"
            return render_template('index.html', alert=alert)

        return render_template('index.html', movies=r.json()['Search'])

    elif request.method == 'POST':
        # get the value of the input with name 'movie' and add it to database
        movie = request.form['movie']
        # add movie to database
        new_movie = Movie(Title=movie)
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/ajout/<IDimdb>')
def ajout(IDimdb):
    payload = { 'i': IDimdb,'apikey': 'ffc487eb'}
    r = requests.get('https://www.omdbapi.com/', params=payload)
    print(r.json())
    new_movie = Movie(Title=r.json()['Title'], Year=r.json()['Year'], imdbID=r.json()['imdbID'], Poster=r.json()['Poster'])
    db.session.add(new_movie)
    db.session.commit()
    alert = "Le film a bien été ajouté"
    return render_template('index.html', alert=alert)

@app.route('/to_download')
def to_download():
    movies = Movie.query.all()
    return render_template('a_telecharger.html', added_movies=movies)


@app.route('/delete/<imdbid>')
def delete(imdbid):
    movie = Movie.query.filter_by(imdbID=imdbid).first()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('to_download'))

if __name__ == '__main__':
    app.run()
