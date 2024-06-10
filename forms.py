from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from wtforms.widgets import html_params, Input
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

class DatePickerWidget(Input):
    input_type = 'text'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('data-provide', 'datepicker')
        kwargs.setdefault('data-date-format', 'yyyy-mm-dd')
        return Markup(f'<input type="{self.input_type}" name="{field.name}" id="{field.id}" value="{field._value()}" {self.html_params(**kwargs)}>')



class MarketForm(FlaskForm):
    market = StringField('Market name', validators=[DataRequired()])
    link = StringField('Location as google maps link',
                       validators=[DataRequired(), URL(require_tld=True, message="This is not URL")])
    open_t = StringField('Open ("12:00" - time format")', widget=TimePickerWidget(), validators=[DataRequired()])
    close_t = StringField('Close ("12:00" - time format")', widget=TimePickerWidget(), validators=[DataRequired()])
    assortment = SelectField('Assortment availability', choices=[('🪚'), ('🪚⚒️'), ('🪚⚒️🖌️')])
    prices = SelectField('Price rate', choices=[('💸'), ('💵'), ('💵💵'), ('💵💵💵'), ('💰💰💰')])
    personnel = SelectField('Personel help', choices=[('🤬'), ('😠'), ('😉'), ('🤩')])
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


class PlaylistForm(FlaskForm):
    username = StringField('Your name / nickname')
    date = StringField('Date', widget=DatePickerWidget(), validators=[DataRequired()])
    submit = SubmitField('Add market', render_kw={'onclick': 'return confirmSubmission();'})
