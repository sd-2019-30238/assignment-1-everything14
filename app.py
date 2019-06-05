#imports
import psycopg2
import hashlib
from flask import Flask, render_template, json, request, session, redirect, send_from_directory
from werkzeug import generate_password_hash, check_password_hash

import datetime


#initialize the flask and SQL Objects
app = Flask(__name__, template_folder="static/templates")

#initializa secret key
app.secret_key='This is my secret key'

connection_parameters = {
        'host':"localhost",
        'database': 'postgres',
        'user': "postgres",
        'password': "docker"
    }

#define methods for routes (what to do and display)
@app.route("/")
def main():
	_user = session.get("user")
	if _user:
		return render_template('servicii.html', id =_user[0], username=_user[1])
	else:
		return render_template('servicii.html', id = 0, username = 0)

@app.route("/index")
def showIndex():
	_user = session.get("user")
	if _user:
		return render_template('servicii.html', id =_user[0], username=_user[1])
	else:
		return render_template('servicii.html', id = 0, username = 0)

@app.route('/showSignup')
def showSignUp():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/addArticleForm')
def addArticleForm():
	_user = session.get("user")
	if _user:
		return render_template('addArticle.html')
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@app.route('/despreNoi')
def showDespreNoi():
	_user = session.get("user")
	if _user:
		return render_template('despreNoi.html', id =_user[0], username=_user[1])
	else:
		return render_template('despreNoi.html', id = 0, username = 0)

@app.route('/viewMessages')
def showViewMessages():
	_user = session.get("user")
	if _user:
		return render_template('viewMessages.html', id =_user[0], username=_user[1])
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@app.route('/servicii')
def showServicii():
	_user = session.get("user")
	if _user:
		return render_template('servicii.html', id =_user[0], username=_user[1])
	else:
		return render_template('servicii.html', id = 0, username = 0)

@app.route('/blog')
def showBlog():
	_user = session.get("user")
	if _user:
		return render_template('blog.html', id =_user[0], username=_user[1])
	else:
		return render_template('blog.html', id = 0, username = 0)

@app.route('/contact')
def showContact():
	_user = session.get("user")
	if _user:
		return render_template('contact.html', id =_user[0], username=_user[1])
	else:
		return render_template('contact.html', id = 0, username = 0)

@app.route('/userHome')
def showUserHome():
	_user = session.get("user")
	if _user:
		return render_template('userHome.html', id =_user[0], username=_user[1])
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
	try:
		_username = request.form['inputUsername']
		_password = request.form['inputPassword']
		conn = psycopg2.connect(**connection_parameters)
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

@app.route('/signUp', methods=['POST'])
def signUp():
	"""
	method to deal with creating a new user in the MySQL Database
	"""
	print("signing up user...")
	conn = psycopg2.connect(**connection_parameters)
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



@app.route('/getAllArticles')
def getAllArticles():
	conn = psycopg2.connect(**connection_parameters)
	cursor = conn.cursor()
	try:
		cursor.execute('SELECT id, title, date, text FROM articles')
		articles = cursor.fetchall()
		articles_list = [{"Id": article[0], "Title": article[1], "Date": article[2], "Text": article[3]} for article in articles]

		return json.dumps(articles_list)

	except Exception as e:
		return render_template('error.html', error = str(e))

	finally:
		cursor.close()
		conn.close()


@app.route('/addArticle',methods=['GET', 'POST'])
def addArticle():
	print("in addArticle")
	try:
		_user = session.get('user')
		if _user:
			print(_user)
			_title = request.form['inputTitle']

			_text = request.form['inputText']
			conn = psycopg2.connect(**connection_parameters)
			print("aici %s" % conn)
			cursor = conn.cursor()
			print("aici2 %s" % cursor)
			cursor.execute("INSERT INTO articles (title, text, date, author_id) values (%s, %s, %s, %s)", (_title, _text, datetime.datetime.now(), session.get('user')[0]))
			conn.commit()
		else:
			return render_template('error.html',error = 'Unauthorized Access')
	except Exception as e:
		print("in exception for addArticle")
		return render_template('error.html', error = str(e))

	finally:
		cursor.close()
		conn.close()
	return redirect('/userHome')


@app.route('/<int:id>/viewArticle', methods=('POST',))
def viewArticle(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE id = %s', [id])
    book = cursor.fetchone()
    
    return render_template('viewArticle.html')


@app.route('/<int:id>/deleteArticle', methods=('POST',))
def deleteArticle(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM articles WHERE id = %s', [id])
    conn.commit()

    return redirect('/userHome')




@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('static/css', path)



if __name__ == "__main__":
    app.run()
