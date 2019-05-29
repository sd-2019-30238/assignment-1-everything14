#imports
import psycopg2
import hashlib
from flask import Flask, render_template, json, request, session, redirect, send_from_directory
from werkzeug import generate_password_hash, check_password_hash
from mediator import Mediator, BorrowBookRequest, ReturnBookRequest, SignUpUserRequest, ValidateLogin, GetUserByIdRequest, GetUsers, GetInactiveUsers, ActivateUser, GetUserBooks, AddBook, GetAllBooks, GetBook, DeleteBook
import abc


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


# classes decorator
class Component(metaclass=abc.ABCMeta):
    """
    Define the interface for objects that can have responsibilities
    added to them dynamically.
    """

    @abc.abstractmethod
    def getAvailability(self):
        pass

class BookClass(Component):
    """
    Define an object to which additional responsibilities can be
    attached.
    """

    def getAvailability(self):
        return "Book"

class Decorator(Component, metaclass=abc.ABCMeta):
    """
    Maintain a reference to a Component object and define an interface
    that conforms to Component's interface.
    """

    def __init__(self, book, ownership):
        self.book = book
        self.book.ownership = ownership

    def getAvailability(self):
        return self.book.getAvailability()

class BorrowedDecorator(Decorator):
    """
    Add responsibilities to the component.
    """

    def __init__(self, book):
        Decorator.__init__(self, book, "Borrowed")

    def getAvailability(self):
        return self.getAvailability() + " : " + book.ownership

class UnavailableDecorator(Decorator):
    """
    Add responsibilities to the component.
    """

    def __init__(self, book):
        Decorator.__init__(self, book, "Unavailable")

    def getAvailability(self):
        return self.getAvailability() + " : " + book.ownership


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
	mediator = Mediator()

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

			method = SignUpUserRequest(conn, cursor, _name, _hashed_password, _email, _pricingPlan)
			mediator.execute(method)
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
		mediator = Mediator()
		
		method = ValidateLogin(cursor, _username)
		users = mediator.execute(method)

		print(users)

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
		return render_template('error.html', error = 'Missing Username or Password')

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
    mediator = Mediator()

    method = GetUserByIdRequest(cursor, id)
    user = mediator.execute(method)
    
    return user

@app.route('/getUsers')
def getUsers():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    mediator = Mediator()

    try:
        _user = session.get('user')
        if _user and (_user[6] == "admin"):
            
            method = GetUsers(cursor)
            users = mediator.execute(method)

            users_list = [{"Id": user[0], "Username": user[1], "Email": user[2], "PricePlan": user[3]} for user in users]

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
    mediator = Mediator()

    try:
        _user = session.get('user')
        if _user and (_user[4] == "librarian"):
            
            method = GetInactiveUsers(cursor)
            users = mediator.execute(method)

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
    mediator = Mediator()

    method = ActivateUser(conn, cursor, id)
    mediator.execute(method)

    return redirect('/userHome')

@app.route('/getUserBooks', methods=('GET',))
def getUserBooks():
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    mediator = Mediator()

    try:
        _user = session.get('user')
        if _user:
            
            method = GetUserBooks(cursor, _user)
            books = mediator.execute(method)

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
            mediator = Mediator()
            
            method = ActivateUser(conn, cursor, [_title, _author, _genre])
            mediator.execute(method)
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
    mediator = Mediator()

    try:
        _user = session.get('user')
        if _user:
            method = GetAllBooks(cursor)
            books = mediator.execute(method)
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
    method = GetBook(cursor, id)
    book = mediator.execute(method)
    
    return book

@app.route('/<int:id>/deleteBook', methods=('POST',))
def deleteBook(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    
    method = DeleteBook(conn, cursor, id)
    mediator.execute(method)

    return redirect('/userHome')

@app.route('/<int:id>/viewBook')
def viewBook(id):
    if session.get("user"):
        return render_template('viewBook.html', )
    else:
        return render_template('error.html', error = "Invalid User Credentials")





@app.route('/<int:id>/borrowBook', methods=('POST',))
def borrowBook(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    mediator = Mediator()

    _user = session.get("user")
    if _user:
        method = BorrowBookRequest(id, conn, cursor, _user)
        if mediator.execute(method):
            cursor.close()
            conn.close()
            return render_template('userLibrary.html', user=_user)
        else:
            cursor.close()
            conn.close()
            return render_template('error.html', error = "Book not available. You've been added to the waiting list")
    else:
        cursor.close()
        conn.close()
        return render_template('error.html', error = "Invalid User")

@app.route('/<int:id>/returnBook', methods=('POST',))
def returnBook(id):
    conn = psycopg2.connect(**connection_parameters)
    cursor = conn.cursor()
    mediator = Mediator()

    _user = session.get("user")
    if _user:
        method = ReturnBookRequest(id, conn, cursor, _user)
        mediator.execute(method)
        cursor.close()
        conn.close()
        return render_template('userLibrary.html', user=_user)
    else:
        cursor.close()
        conn.close()
        return render_template('error.html', error = "Invalid User")

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('view/static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('view/static/css', path)



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
