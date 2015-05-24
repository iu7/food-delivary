from flask import Flask, request,render_template, redirect
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import Required, Length
from datetime import date
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from random import randint
from time import sleep
from flask import jsonify, session
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SomeNotVerySeriousSecretKeyForDebugVersion'
bootstrap = Bootstrap(app)
CsrfProtect(app)

class CardData(Form):
	valid_thru_year = SelectField('Year', coerce=int, choices=[(x,x) for x in range(date.today().year, date.today().year+10)])
	valid_thru_month = SelectField('Month', coerce=int, choices=[(x,x) for x in range(1,13)])
	card_number = StringField('Card number', [Length(min=16, max=16,message='Card number must contain 16 digits')])
	card_holder_name = StringField('Card holder name', [Required()])
	cv_code = PasswordField('CVC/CVV', [Length(min=3, max=3, message='Code must contain 3 digits')])

@app.route('/')
def index():
	return 'Payment dummy service'

@app.route('/payment/dummy', methods=['POST', 'GET'])
def payment_online():
	#session_id = request.cookies.get('session_id')
	form = CardData()
	if form.validate_on_submit():
		sleep(randint(2,5))
		redirect_uri = session['redirect_uri']
		redirect_uri += '?operation=payment&status=accepted&card_number=****'+\
			str(form.data.get('card_number')[-4:])+'&card_holder_name='+str(form.data.get('card_holder_name'))
		return redirect(redirect_uri, 302)
	redirect_uri = request.args.get('redirect_uri')
	if not redirect_uri:
		return jsonify(result='Incorrect request'), 400
	else:
		session['redirect_uri'] = redirect_uri
	return render_template('payment.html', form=form, redirect_uri=redirect_uri)

if __name__ == '__main__':
	app.run(debug=True, port=5050)
