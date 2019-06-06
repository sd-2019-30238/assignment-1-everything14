from flask import Blueprint, send_from_directory


send = Blueprint('send', __name__, template_folder="static/templates")


@send.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('static/js', path)

@send.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('static/css', path)