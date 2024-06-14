import os
import io
import base64
from flask import Flask,  render_template, redirect, url_for,  request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
import qrcode

from morse import generate_morse
from tictactoe import restart_game, change_image, player_move, computer_move
import csv
from forms import MarketForm, PlaylistForm
from spotify_agent import find_and_generate_playlist



tictactoe_images = restart_game()
moves = 9
all_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8]

app = Flask(__name__)
key = os.environ.get('FLASK')
app.config['SECRET_KEY'] = key

ckeditor = CKEditor(app)
Bootstrap5(app)


def gen_qr_by_link(link: str):
    img = qrcode.make(link, border=0)
    # img.save("static/temp/temp_qr.png")
    # img_url = url_for('static', filename="/temp/temp_qr.png")
    # return img_url
    # Save the image to a bytes buffer
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    # Encode the image to base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


def cards_state():
    cards = {0: '', 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: ''}
    return cards


def disable_all_cards(cards):
    for card in cards:
        cards[card] = "pointer-events: none;"
    return cards


card_dict = cards_state()


def disable_card(card_dict, ind: int):
    card_dict[ind] = "pointer-events: none;"
    return card_dict


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
    global tictactoe_images, win_text, moves, all_cards, card_dict
    print(f'Card Dict: {card_dict}')
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
        disable_card(card_dict, image_id)
        # Player Move
        game_is_over = player_move(image_id)
        tictactoe_images = change_image(image_id, 1, tictactoe_images)
        moves -= 1
        if game_is_over:
            win_text = "✨✨ You Win! ✨✨"
            disable_all_cards(card_dict)
            return render_template("tictactoe.html", images=tictactoe_images, is_over=game_is_over, win_text=win_text,
                                   card_dict=card_dict)

        if moves > 1:
            # Computer move
            image_id, game_is_over = computer_move()
            moves -= 1
            if image_id is not None:
                tictactoe_images = change_image(image_id, 2, tictactoe_images)
                win_text = "Python script wins 🤖!"
                all_cards.remove(image_id)
                disable_card(card_dict, image_id)
                if game_is_over:
                    disable_all_cards(card_dict)
            return render_template("tictactoe.html", images=tictactoe_images, is_over=game_is_over, win_text=win_text,
                                   card_dict=card_dict)
        else:
            game_is_over = True
            disable_all_cards(card_dict)
            win_text = "☀️ DRAW! 🌚"
            return render_template("tictactoe.html", images=tictactoe_images, is_over=game_is_over, win_text=win_text,
                                   card_dict=card_dict)

    moves = 9
    all_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    tictactoe_images = restart_game()
    card_dict = cards_state()
    return render_template("tictactoe.html", images=tictactoe_images, card_dict=card_dict)

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

        # img_url = gen_qr_by_link(link)
        link = find_and_generate_playlist(name, input_date)
        img_base64 = gen_qr_by_link(link)

        # Create the data URL for the base64 string
        img_url = f"data:image/png;base64,{img_base64}"

        return render_template('playlist_done.html', img_url=img_url, link=link)
    return render_template('playlist.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)
