from flask import render_template
from . import main
from flask import jsonify
from .. exceptions import UException

@main.app_errorhandler(UException)
def handle_invalid_usage(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response

@main.app_errorhandler(Exception)
def handle_exception(error):
	response = jsonify(message='Unexpected server error', payload=error.message, doc=error.__doc__), 500
	return response


@main.app_errorhandler(404)
def page_not_found(e):
	return 'page not found'	
#return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
