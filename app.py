import os
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
    Poster = db.Column(db.text)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        # ask API for movies that return a json to store on a variable



    return render_template('index.html')

@app.route('/to_download')
def download_film():

    added_movie = Movie.query.all()
    print(added_movie[0])
    return render_template('a_telecharger.html', added_movies=added_movie)

if __name__ == '__main__':
    app.run()
