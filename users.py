import hashlib
from flask import json, Blueprint, request, session, render_template, redirect
from werkzeug import generate_password_hash, check_password_hash
from dbAccess import getConn


users = Blueprint('users', __name__, template_folder="static/templates")

@users.route('/showSignup')
def showSignUp():
	return render_template('signup.html')

@users.route('/login')
def login():
	return render_template('login.html')

@users.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')

@users.route('/validateLogin', methods=['POST'])
def validateLogin():
	try:
		_username = request.form['inputUsername']
		_password = request.form['inputPassword']
		conn = getConn()
		cursor = conn.cursor()

		cursor.execute("SELECT * from users where username = %s", [_username])
		users = cursor.fetchall()
		#acctually validate these users
		if len(users)>0:
			_hashed_password = hashlib.md5(_password.encode('utf-8')).hexdigest()
			if users[0][2] == _hashed_password:
				session['user']=users[0]
				return redirect('/userHome')
			else:
				return render_template('error.html', error="incorrect username or password")
		else:
			return render_template('error.html', error= "incorrect username or password")

	except Exception as ex:
		print("Error getting username and password, Error:", ex)
		return render_template('error.html', error = 'Missing Email Adress or Password')

	finally:
		cursor.close()
		conn.close()

@users.route('/signUp', methods=['POST'])
def signUp():
	"""
	method to deal with creating a new user in the MySQL Database
	"""
	print("signing up user...")
	conn = getConn()
	#create a cursor to query the stored procedure
	cursor = conn.cursor()

	try:
		#read in values from frontend
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']

		#Make sure we got all the values
		if _name and _email and _password:
			print("Email:", _email, "\n", "Name:", _name, "\n", "Password:", _password)
			#hash passowrd for security
			_hashed_password = hashlib.md5(_password.encode('utf-8')).hexdigest()
			print("Hashed Password:", _hashed_password)

			#call jQuery to make a POST request to the DB with the info
			cursor.execute('INSERT INTO users (username, password, email) values (%s, %s, %s)', [_name, _hashed_password, _email])
			conn.commit()

		else:
			print('fields not submitted')
			return 'Enter the required fields'

	except Exception as ex:
		print('got an exception: ', ex)
		return json.dumps({'error':str(ex)})

	finally:
		print('ending...')
		cursor.close()
		conn.close()
	return "OK"