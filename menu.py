from flask import json, Blueprint, request, session, render_template


menu = Blueprint('menu', __name__, template_folder="static/templates")


@menu.route("/")
@menu.route("/index")
def main():
	_user = session.get("user")
	if _user:
		return render_template('index.html', id =_user[0], username=_user[1])
	else:
		return render_template('index.html', id = 0, username = 0)

@menu.route('/despreNoi')
def showDespreNoi():
	_user = session.get("user")
	if _user:
		return render_template('despreNoi.html', id =_user[0], username=_user[1])
	else:
		return render_template('despreNoi.html', id = 0, username = 0)

@menu.route('/viewMessages')
def showViewMessages():
	_user = session.get("user")
	if _user:
		return render_template('viewMessages.html', id =_user[0], username=_user[1])
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@menu.route('/servicii')
def showServicii():
	_user = session.get("user")
	if _user:
		return render_template('servicii.html', id =_user[0], username=_user[1])
	else:
		return render_template('servicii.html', id = 0, username = 0)

@menu.route('/blog')
def showBlog():
	_user = session.get("user")
	if _user:
		return render_template('blog.html', id =_user[0], username=_user[1])
	else:
		return render_template('blog.html', id = 0, username = 0)

@menu.route('/contact')
def showContact():
	_user = session.get("user")
	if _user:
		return render_template('contact.html', id =_user[0], username=_user[1])
	else:
		return render_template('contact.html', id = 0, username = 0)

@menu.route('/userHome')
def showUserHome():
	_user = session.get("user")
	if _user:
		return render_template('userHome.html', id =_user[0], username=_user[1])
	else:
		return render_template('error.html', error = "Invalid User Credentials")
