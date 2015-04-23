from flask import Flask, request,render_template
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import Required, Length
from datetime import date
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SomeNotVerySeriousSecretKeyForDebugVersion'
bootstrap = Bootstrap(app)

class CardData(Form):
	valid_thru_year = SelectField('Year', coerce=int, choices=[(x,x) for x in range(date.today().year, date.today().year+10)])
	valid_thru_month = SelectField('Month', coerce=int, choices=[(x,x) for x in range(1,13)])
	card_number = StringField('Card number', [Required()])
	card_holder_name = StringField('Card holder name', [Required()])
	cv_code = PasswordField('CVC/CVV', [Length(min=3, max=3)])

@app.route('/')
def index():
	return 'Payment dummy service'

@app.route('/payment/dummy', methods=['POST', 'GET'])
def payment_online():
	form = CardData()
	if form.validate_on_submit():
		return 'hello'
	return render_template('payment.html', form=form)

if __name__ == '__main__':
	app.run(debug=True, port=5050)
