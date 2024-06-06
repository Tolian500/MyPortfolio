from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv
from wtforms.widgets import html_params
from markupsafe import Markup

class TimePickerWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'text')
        html = f'''
        <div class="input-group mb-3" id="{field.id}_group">
            <input {html_params(name=field.name, **kwargs)} class="form-control timePicker">
            <div class="input-group-append">
                <button class="btn btn-outline-secondary" type="button"><i class="fa fa-clock-o"></i></button>
            </div>
        </div>
        '''
        return Markup(html)


# class TimePickerWidget(object):
#     def __call__(self, field, **kwargs):
#         kwargs.setdefault('id', field.id)
#         kwargs.setdefault('type', 'text')
#         html = f'''
#         <div class="input-group mb-3" id="{field.id}_group">
#             <div class="input-group-prepend">
#                 <button class="btn btn-outline-secondary" type="button">Button</button>
#             </div>
#             <input {html_params(name=field.name, **kwargs)} class="form-control timePicker">
#         </div>
#         '''
#         return Markup(html)



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class MarketForm(FlaskForm):
    market = StringField('Market name', validators=[DataRequired()])
    link = StringField('Location as google maps link', validators=[DataRequired(), URL(require_tld=True, message="This is not URL")])
    open_t = StringField('Open ("12:00" - time format")', widget=TimePickerWidget(), validators=[DataRequired()])
    close_t = StringField('Close ("12:00" - time format")', widget=TimePickerWidget(), validators=[DataRequired()])
    assortment = SelectField('Assortment availability', choices=[('🪚'),('🪚⚒️'),('🪚⚒️🖌️')])
    prices = SelectField('Price rate', choices=[('💸'),('💵'),('💵💵'),('💵💵💵'),('💰💰💰')])
    personnel = SelectField('Personel help', choices=[('🤬'),('😠'),('😉'),('🤩')])
    submit = SubmitField('Add market', render_kw={'onclick': 'return confirmSubmission();'})

    def __init__(self, *args, **kwargs):
        super(MarketForm, self).__init__(*args, **kwargs)

        # Add JavaScript to the form template
        self.js_script = '''
        <script>
            function confirmSubmission() {
                return confirm("Are you sure you want to submit the new market?");
            }
        </script>
        '''

    def __call__(self):
        return self.js_script + super(MarketForm, self).__call__()

#
def add_market_data(new_data:list):
    with open('market-data.csv', newline='', encoding='utf-8') as csv_file:
        prev_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in prev_data:
            list_of_rows.append(row)
    print(list_of_rows)
    list_of_rows.append(new_data)
    with open('market-data.csv', newline='', encoding='utf-8',mode="w") as csv_file:
        wr = csv.writer(csv_file)
        wr.writerows(list_of_rows)


# Exercise:
# add: Location URL, open time, closing time, coffee rating, wifi rating, power outlet rating fields
# make coffee/wifi/power a select element with choice of 0 to 5.
# e.g. You could use emojis ☕️️️️/💪/✘/🔌
# make all fields required except submit
# use a validator to check that the URL field has a URL entered.
# ---------------------------------------------------------------------------


# all Flask routes below
@app.route("/markets")
def markets_home():
    return render_template("markets_main.html")

#
@app.route('/add', methods=['GET', 'POST'])
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
#
#
@app.route('/cafes')
def markets():
    with open('market-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('markets.html', markets=list_of_rows)
#

if __name__ == '__main__':
    app.run(debug=True)