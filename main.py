from datetime import date
import os
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from morse import generate_morse
from tictactoe import restart_game, change_image, player_move, computer_move

# Optional: add contact me email functionality (Day 60)
# import smtplib

tictactoe_images = restart_game()
moves = 9
all_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8]
print(all_cards)
'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)

# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')

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


if __name__ == "__main__":
    app.run(debug=True, port=5001)
