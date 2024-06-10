from datetime import date
import os
from flask import Flask, abort, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from morse import generate_morse
from tictactoe import restart_game, change_image, player_move, computer_move
import csv
from forms import MarketForm, PlaylistForm
from spotify_agent import find_and_generate_playlist

# Optional: add contact me email functionality (Day 60)
# import smtplib

tictactoe_images = restart_game()
moves = 9
all_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8]

app = Flask(__name__)
key = os.environ.get('FLASK')
print(f"Flask key = {key}")
app.config['SECRET_KEY'] = key

ckeditor = CKEditor(app)
Bootstrap5(app)


@app.route('/')
def main_page():
    return render_template("index.html", )


@app.route('/projects/morse', methods=["GET", "POST"])
def morse_project():
    if request.method == 'POST':
        user_input = request.form['morse_input']
        morse_code = generate_morse(user_input)
        return render_template("morse.html", user_input=user_input, morse_output=morse_code)
    return render_template("morse.html")


@app.route('/projects/tictactoe', methods=["GET", "POST"])
def tictactoe_game():
    global tictactoe_images, win_text, moves, all_cards
    image_id = request.args.get("id")

    print(image_id)
    if image_id == "100":
        tictactoe_images = restart_game()
        print("Restart")
        print(tictactoe_images)
        return redirect(url_for("tictactoe_game"))
    if image_id is not None:
        image_id = int(image_id)
        if int(image_id) not in all_cards:
            return render_template("tictactoe.html", images=tictactoe_images)
        all_cards.remove(image_id)
        # Player Move
        game_is_over = player_move(image_id)
        tictactoe_images = change_image(image_id, 1, tictactoe_images)
        moves -= 1
        if game_is_over == True:
            win_text = "✨✨ You Win! ✨✨"
            return render_template("tictactoe.html", images=tictactoe_images, is_over=game_is_over, win_text=win_text)

        if moves > 1:
            # Computer move
            image_id, game_is_over = computer_move()
            moves -= 1
            if image_id is not None:
                tictactoe_images = change_image(image_id, 2, tictactoe_images)
                win_text = "Python script wins 🤖!"
            return render_template("tictactoe.html", images=tictactoe_images, is_over=game_is_over, win_text=win_text)
        else:
            game_is_over = True
            win_text = "☀️ DRAW! 🌚"
            return render_template("tictactoe.html", images=tictactoe_images, is_over=game_is_over, win_text=win_text)

    moves = 9
    all_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    tictactoe_images = restart_game()
    return render_template("tictactoe.html", images=tictactoe_images)

    # MARKETS SECTION


def add_market_data(new_data: list):
    with open('market-data.csv', newline='', encoding='utf-8') as csv_file:
        prev_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in prev_data:
            list_of_rows.append(row)
    print(list_of_rows)
    list_of_rows.append(new_data)
    with open('market-data.csv', newline='', encoding='utf-8', mode="w") as csv_file:
        wr = csv.writer(csv_file)
        wr.writerows(list_of_rows)


@app.route("/markets/home")
def markets_home():
    return render_template("markets_main.html")


@app.route('/markets')
def markets():
    with open('market-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('markets.html', markets=list_of_rows)


@app.route('/markets/add', methods=['GET', 'POST'])
def addMarket():
    form = MarketForm()
    if form.validate_on_submit():
        print("True")
    # Exercise:
    # Make the form write a new row into cafe-data.csv
    # with   if form.validate_on_submit()
    if form.validate_on_submit():
        new_datalist = [
            form.market.data,
            form.link.data,
            form.open_t.data,
            form.close_t.data,
            form.assortment.data,
            form.prices.data,
            form.personnel.data
        ]
        print(form.market.data)
        add_market_data(new_datalist)
        return markets()

    return render_template('add_market.html', form=form)


# SpotifyPlaylist Form
@app.route('/projects/playlist', methods=['GET', 'POST'])
def playlist():
    form = PlaylistForm()
    if request.method == 'POST':
        print(request.form)
        name = request.form['username']
        if len(name) <= 0:
            name = "Time Traveler"
        input_date = request.form["date"]
        print(name, input_date)
        return jsonify({'name': name, 'date': input_date})
        # Change later to the code below
        # return find_and_generate_playlist(name, input_date)
    return render_template('playlist.html', form=form)


@app.route('/projects/playalt', methods=['GET', 'POST'])
def playalt():
    form = PlaylistForm()
    if request.method == 'POST':
        print(request.form)
        name = request.form['username']
        if len(name) <= 0:
            name = "Time Traveler"
        input_date = request.form["date"]
        print(name, input_date)
        # return jsonify({'name': name, 'date': input_date})
        # Change later to the code below
        return redirect(find_and_generate_playlist(name, input_date))
    return render_template('playalt.html', target="blank")

@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
