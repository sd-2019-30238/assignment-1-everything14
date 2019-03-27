#imports
import psycopg2
import hashlib
from flask import Flask, render_template, json, request, session, redirect
from werkzeug import generate_password_hash, check_password_hash


#initialize the flask and SQL Objects
app = Flask(__name__, template_folder="view/static/templates")

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
    return render_template('index.html')

@app.route("/main")
def return_main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
	return render_template('signup.html')

@app.route('/showSignIn')
def showSignIn():
	return render_template('signin.html')

@app.route('/wishlist')
def wishlist():
	return render_template('wishlist.html')

@app.route('/userHome')
def showUserHome():
	#check that someone has logged in correctly
	if session.get("user"):
		return render_template('userHome.html', username=session.get("user")[1])
	else:
		return render_template('error.html', error = "Invalid User Credentials")


@app.route('/signUp', methods=['POST'])
def signUp():
	"""
	method to deal with creating a new user in the Postgre Database
	"""
	print("signing up user...")
	#create MySQL Connection
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
			cursor.execute('INSERT INTO users (username, password, email, role) values (%s, %s, %s, \'user\')', [_name, _hashed_password, _email])
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


@app.route('/validateLogin', methods=['POST'])
def validate():
	try:
		_username = request.form['inputUsername']
		_password = request.form['inputPassword']
		print("Username:", _username, "\n Password:", _password)

		#create Postgres Connection
		conn = psycopg2.connect(**connection_parameters)
		#create a cursor to query the stored procedure
		cursor = conn.cursor()
		print("successfully connected to postgres!")

		#get users with this username (should only be one)
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


@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')


@app.route('/addBook',methods=['POST'])
def addBook():
    print("in addBook")
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _genre = request.form['inputGenre']
            _author = request.form['inputAuthor']
            _user = session.get('user')[0]
            print("title:",_title,"\n genre:",_genre, "\n author: ", _author, "\n user:",_user)
            conn = psycopg2.connect(**connection_parameters)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author, genre, available) values (%s, %s, %s, True)", (_title, _author, _genre))
            conn.commit()
 
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        print("in exception for AddBook")
        return render_template('error.html',error = str(e))

    finally:
        cursor.close()
        conn.close()
    return redirect('/userHome')


@app.route('/getBooks')
def getBooks():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _user = session.get('user')[0]
            print(_user)
            cursor.execute('SELECT id, title, author, genre FROM books')
            books = cursor.fetchall()

            books_list = [{"Id": book[0], "Title": book[1], "Author": book[2], "Genre": book[3]} for book in books]

            print(books_list)
            return json.dumps(books_list)

        else:
            return render_template('error.html', error = 'Unauthorized Access')

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
    	cursor.close()
    	conn.close()

@app.route('/<int:id>/getBook', methods=('POST',))
def getBook(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = %s', [id])
    book = cursor.fetchone()
    
    return book

@app.route('/<int:id>/deleteBook', methods=('POST',))
def deleteBook(id):
    getBook(id)
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s', [id])
    conn.commit()

    return redirect('/userHome')

@app.route('/<int:id>/viewBook')
def viewBook(id):
    if session.get("user"):
        return render_template('viewBook.html', )
    else:
        return render_template('error.html', error = "Invalid User Credentials")

def insertTestData():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, genre, available) values ('a', 'a', 'a', True)")
    cursor.execute("INSERT INTO books (title, author, genre, available) values ('b', 'b', 'b', True)")
    cursor.execute("INSERT INTO books (title, author, genre, available) values ('c', 'c', 'c', True)")
    cursor.execute("INSERT INTO books (title, author, genre, available) values ('d', 'd', 'd', True)")
    cursor.execute("INSERT INTO books (title, author, genre, available) values ('e', 'e', 'e', True)")
    conn.commit()


if __name__ == "__main__":
    # insertTestData()
    app.run()
