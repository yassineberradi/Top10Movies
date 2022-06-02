import os

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from dataManager import DataManager, MOVIE_DB_IMAGE_URL, MOVIE_DB_INFO_URL, API_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///movies.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MovieInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# db.create_all()
#
# new_movie = MovieInfo(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


class EditForm(FlaskForm):
    rating = StringField("Your Rating Out of 10.", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done!")


class AddForm(FlaskForm):
    title = StringField("Movie Name:", validators=[DataRequired()])
    submit = SubmitField("Done!")


@app.route("/")
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = MovieInfo.query.order_by(MovieInfo.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    edit_form = EditForm()
    movie_id = request.args.get('id')
    movie = MovieInfo.query.get(movie_id)
    if edit_form.validate_on_submit():
        movie.review = edit_form.review.data
        movie.rating = float(edit_form.rating.data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=edit_form, movie=movie)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_movie = AddForm()
    data_manager = DataManager()
    if add_movie.validate_on_submit():
        movie_name = add_movie.title.data
        movies_from_api = data_manager.get_data(movie_name)
        return render_template('select.html', movies=movies_from_api)
    return render_template('add.html', form=add_movie)


@app.route("/select", methods=["GET", "POST"])
def select():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        # The language parameter is optional, if you were making the website for a different audience
        # e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        print(data)
        new_movie = MovieInfo(
            title=data["title"],
            year=int(data["release_date"].split("-")[0]),
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = MovieInfo.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
