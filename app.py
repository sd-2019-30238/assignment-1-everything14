#imports
import psycopg2
import hashlib
from flask import Flask, render_template, json, request, session, redirect, send_from_directory
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

#classes
class Recommendations(object):
    def factory(type):
        #return eval(type + "()")
        if type == "Genres":
            return Genres()
        if type == "Trends":
            return Trends()
        if type == "Topics":
            return Topics()
        assert 0, "Bad recommendation creation: " + type
        
    factory = staticmethod(factory)
 
def listToDict(items):
    stats = dict()
    for i in items:
        if i in stats:
            stats[i] += 1
        else:
            stats[i] = 1
    return stats

class Genres(Recommendations):
    def getRecommendations(self):
        _user = session.get('user')

        conn = psycopg2.connect(**connection_parameters)
        cursor = conn.cursor()

        cursor.execute('SELECT id_book FROM borrows WHERE id_user = %s', [_user[0]])
        user_borrows = cursor.fetchall()
    
        user_genres = list()
        for i in range(len(user_borrows)):
            cursor.execute('SELECT genre FROM books WHERE id = %s', [user_borrows[i][0]])
            user_genres.append(cursor.fetchone()[0])

        genre_dict = listToDict(user_genres)

        cursor.execute('SELECT id, title, author, genre FROM books WHERE genre = %s', [max(genre_dict, key=genre_dict.get)])
        recos = cursor.fetchall()
        return recos[:5]
 
class Trends(Recommendations):
    def getRecommendations(self):
        _user = session.get('user')

        conn = psycopg2.connect(**connection_parameters)
        cursor = conn.cursor()

        cursor.execute('SELECT id_book FROM borrows WHERE id_user != %s', [_user[0]])
        latest_borrows = cursor.fetchall()[-5:]

        recos = list()
        for i in range(len(latest_borrows)):
            cursor.execute('SELECT id, title, author, genre FROM books WHERE id = %s', [latest_borrows[i]])
            recos.append(cursor.fetchone())
        
        return recos

class Topics(Recommendations):
    def getRecommendations(self):
        #here i didn't know what is this about :-?
        return

def recommendationsGen():
    types = Recommendations.__subclasses__()
    for t in types[:2]:
        yield t.__name__

def getUserRecommendations():
    recommendations = [Recommendations.factory(i) for i in recommendationsGen()]

    recos = list()
    for recommendation in recommendations:
        for rec in recommendation.getRecommendations():
            recos.append(rec)
    print(recos)
    return recos

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

@app.route('/allBooks')
def allBooks():
    _user = session.get("user")
    if _user:
        if _user[6] == True:
            if _user[4] == "user":
                return render_template('allBooks.html', user=_user)
            else:
                return render_template('error.html', error = "Invalid User")
        else:
            return render_template('error.html', error = "User payment not confirmed")
    else:
        return render_template('error.html', error = "Invalid User")

@app.route('/userHome')
def showUserHome():
	#check that someone has logged in correctly
    _user = session.get("user")
    if _user:
        if _user[6] == True:
            if _user[4] == "librarian":
                return render_template('userHomeLibrarian.html', user=_user)
            elif _user[4] == "user":
                return render_template('userHomeUser.html', user=_user)
            elif _user[4] == "admin":
                print("admin")
                return render_template('userHomeUser.html', user=_user)
        else:
            return render_template('error.html', error = "User payment not confirmed")
    else:
        return render_template('error.html', error = "Invalid User")

@app.route('/userLibrary')
def userLibrary():
	#check that someone has logged in correctly
    _user = session.get("user")
    if _user:
        if _user[6] == True:
            if _user[4] == "user":
                return render_template('userLibrary.html', user=_user)
            else:
                return render_template('error.html', error = "Invalid User")
        else:
            return render_template('error.html', error = "User payment not confirmed")
    else:
        return render_template('error.html', error = "Invalid User")



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
		_pricingPlan = request.form['inputPricePlan']

		#Make sure we got all the values	
		if _name and _email and _password:
			print("Email:", _email, "\n", "Name:", _name, "\n", "Password:", _password)
			#hash passowrd for security
			_hashed_password = hashlib.md5(_password.encode('utf-8')).hexdigest()
			print("Hashed Password:", _hashed_password)

			#call jQuery to make a POST request to the DB with the info
			cursor.execute('INSERT INTO users (username, password, email, role, price_plan, approved_user) values (%s, %s, %s, \'user\', %s, False)', [_name, _hashed_password, _email, _pricingPlan])
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

@app.route('/<int:id>/getUser', methods=('POST',))
def getUser(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', [id])
    user = cursor.fetchone()
    
    return user

@app.route('/getUsers')
def getUsers():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        _user = session.get('user')
        if _user and (_user[6] == "admin"):
            cursor.execute('SELECT id, username, email, price_plan FROM users')
            users = cursor.fetchall()

            users_list = [{"Id": user[0], "Username": user[1], "Email": user[2], "PricePlan": user[3]} for user in users]

            print(users_list)
            return json.dumps(users_list)

        else:
            return render_template('error.html', error = 'Unauthorized Access')

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
    	cursor.close()
    	conn.close()

@app.route('/getInactiveUsers')
def getInactiveUsers():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        _user = session.get('user')
        if _user and (_user[4] == "librarian"):
            cursor.execute('SELECT id, username, email, price_plan, approved_user FROM users WHERE approved_user = False')
            users = cursor.fetchall()

            users_list = [{"Id": user[0], "Username": user[1], "Email": user[2], "PricePlan": user[3], "ApprovedUser": user[4]} for user in users]
            return json.dumps(users_list,)

        else:
            return render_template('error.html', error = 'Unauthorized Access')

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
    	cursor.close()
    	conn.close()

@app.route('/<int:id>/activateUser', methods=('POST',))
def activateUser(id):
    getUser(id)
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET approved_user = True WHERE id = %s', [id])
    conn.commit()

    return redirect('/userHome')

@app.route('/getUserBooks', methods=('GET',))
def getUserBooks():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        _user = session.get('user')
        if _user:
            cursor.execute('SELECT id_book FROM borrows WHERE id_user = %s AND status_finished = False', [_user[0]])
            id_books = cursor.fetchall()

            books = list()
            for x in range(len(id_books)):
                cursor.execute('SELECT id, title, author, genre FROM books WHERE id = %s', [id_books[x]])
                book = cursor.fetchall()
                books.append(book[0])

            books_list = [ {"Id": book[0], "Title": book[1], "Author": book[2], "Genre": book[3]} for book in books]
            
            return json.dumps(books_list)

        else:
            return render_template('error.html', error = 'Unauthorized Access')

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
    	cursor.close()
    	conn.close()



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

@app.route('/getAllBooks')
def getAllBooks():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        _user = session.get('user')
        if _user:
            cursor.execute('SELECT id, title, author, genre FROM books')
            books = cursor.fetchall()
            books_list = [{"Id": book[0], "Title": book[1], "Author": book[2], "Genre": book[3]} for book in books]

            return json.dumps(books_list)

        else:
            return render_template('error.html', error = 'Unauthorized Access')

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
    	cursor.close()
    	conn.close()

@app.route('/getRecommendedBooks')
def getRecommendedBooks():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        _user = session.get('user')
        if _user:
            books = getUserRecommendations()
            books_list = [{"Id": book[0], "Title": book[1], "Author": book[2], "Genre": book[3]} for book in books]
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

@app.route('/<int:id>/getBookAvailability', methods=('POST',))
def getBookAvailability(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    cursor.execute('SELECT available FROM books WHERE id = %s', [id])
    bookAvailable = cursor.fetchone()
    
    return bookAvailable



@app.route('/<int:id>/borrowBook', methods=('POST',))
def borrowBook(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()

    _user = session.get("user")
    if _user:
        if getBookAvailability(id):
            cursor.execute('UPDATE books SET available = False WHERE id = %s;', [id])
            cursor.execute('INSERT INTO borrows (id_user, id_book, status_finished) VALUES (%s, %s, False);', [_user[0], id])
            conn.commit()
            return render_template('userLibrary.html', user=_user)
        else: 
            cursor.execute('INSERT INTO waiting_list (id_user, id_book) VALUES (%s, %s)', [_user[0], id])
            conn.commit()
            return render_template('error.html', error = "Book not available. You've been added to the waiting list")
    else:
        return render_template('error.html', error = "Invalid User")

@app.route('/<int:id>/returnBook', methods=('POST',))
def returnBook(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()

    _user = session.get("user")
    if _user:
        cursor.execute('UPDATE books SET available = True WHERE id = %s;', [id])
        cursor.execute('UPDATE borrows SET status_finished = True WHERE id_user = %s AND id_book = %s', [_user[0], id])
        conn.commit()

        cursor.execute('SELECT id_user from waiting_list WHERE id_book = %s', [id])
        userFromWaitingList = cursor.fetchall()
        if userFromWaitingList != []:
            for idUser in userFromWaitingList:
                if idUser not in gSendNotification:
                    gSendNotification[idUser] = list()
            gSendNotification[idUser].append(id)
        return render_template('userLibrary.html', user=_user)
    else:
        return render_template('error.html', error = "Invalid User")


@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('view/static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('view/static/css', path)

gSendNotification = dict()
@app.route('/getNotification')
def getNotification():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    try:
        _user = session.get('user')
        print(_user)
        print(gSendNotification)
        books = list()
        for bookId in gSendNotification[_user[0]]:
            cursor.execute('SELECT id, title, author, genre FROM books WHERE id = %s', [bookId])
            entry = cursor.fetchall()
            print(entry)
            print(entry[0])
            books.append(entry[0])
        books_list = [{"Id": book[0], "Title": book[1], "Author": book[2], "Genre": book[3]} for book in books]
        print(books_list)
        del gSendNotification[_user[0]]
        print(gSendNotification)
        return json.dumps(books_list)

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
    	cursor.close()
    	conn.close()

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
    #getUserRecommendations()
    app.run()
