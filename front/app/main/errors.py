from flask import render_template
from . import main
from flask import abort

@main.app_errorhandler(Exception)
def handle_invalid_usage(error):
	return render_template('500.html'), 500	
	#response = jsonify(error.to_dict())
	#response.status_code = error.status_code
	#return response


@main.app_errorhandler(404)
def page_not_found(e):
	#return '404 test'
	return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

