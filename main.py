import os
from io import BytesIO
import base64
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
import qrcode
import time
from morse import generate_morse
from tictactoe import restart_game, change_image, player_move, computer_move
import csv
from forms import MarketForm, PlaylistForm
from spotify_agent import find_and_generate_playlist
from bybit_manager import BybitManager

tictactoe_images = restart_game()
moves = 9
all_cards = [0, 1, 2, 3, 4, 5, 6, 7, 8]

app = Flask(__name__)
key = os.environ.get('FLASK')
app.config['SECRET_KEY'] = key
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")



ckeditor = CKEditor(app)
Bootstrap5(app)

# DEBUG MODE
DEBUG_MODE = True  # CHANGE BEFORE PRODUCTION


def gen_qr_by_link(link: str):
    img = qrcode.make(link, border=0)
    # img.save("static/temp/temp_qr.png")
    # img_url = url_for('static', filename="/temp/temp_qr.png")
    # return img_url

    # Encode the image directly to base64
    # Use BytesIO to save image data in memory and then encode to base64
    buf = BytesIO()
    img.save(buf)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

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



def get_rsi_data(symbol:str, interval:str, window:int):
    start_time = int((time.time() - 60 * 60 * 24) * 1000)  # 24 hours ago in milliseconds
    end_time = int(time.time() * 1000)  # current time in milliseconds
    manager = BybitManager(API_KEY, API_SECRET, window)

    before_fetch = time.time()
    kline_data = manager.fetch_kline_data(symbol, interval, start_time, end_time)

    # Record the time after fetching data
    after_fetch = time.time()

    # Calculate the delay in milliseconds
    delay_ms = int((after_fetch - before_fetch) * 1000)
    if kline_data:
        # Calculate RSI
        df = manager.calculate_rsi(kline_data)

        # Find first non-NaN RSI value and its timestamp
        first_valid_rsi = df['RSI'].dropna().iloc[0]
        first_valid_time = df.index[df['RSI'].notna()].tolist()[0]
        rsi_message = f"RSI for {symbol}: {first_valid_rsi:.2f} at {first_valid_time.strftime('%Y-%m-%d %H:%M:%S')} (Delay: {delay_ms} ms)"
        return rsi_message






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


@app.route('/photography', methods=['GET', 'POST'])
def ph_main():
    return render_template('ph_index.html')


@app.route('/rsi', methods=['GET', 'POST'])
def rsi_main():
    if request.method == 'POST':

        symbol_mapping = {"BTC/USDT": 'BTCUSDT', "ETH/USDT": 'ETHUSDT', "SOL/USDT": 'SOLUSDT'}
        # interval_mapping = {0: '1', 1: '60', 2: '1440'}
        interval_mapping = {0: '1', 1: '60', 2: 'D'}  # Example for Bybit
        window_mapping = {0: 10, 1: 12, 2: 14, 3: 16, 4: 18}
        symbol_raw = request.form.get('currency')
        interval = interval_mapping[int(request.form.get('timeframe'))]
        window = window_mapping[int(request.form.get('period'))]
        symbol = symbol_mapping[symbol_raw]

        message = get_rsi_data(symbol, interval, window)  # Your function to get RSI data
        print(message)
        # example_value = f"RSI for {symbol}: 75.72 at 2024-06-23 21:00:00 Delay: 281 ms - Current UTC time: 11:00:00 UTC"
        return jsonify({'value': message})

    return render_template('rsi.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=DEBUG_MODE)
