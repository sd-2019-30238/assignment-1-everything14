def getBookAvailability(id, cursor):
    cursor.execute('SELECT available FROM books WHERE id = %s', [id])
    bookAvailable = cursor.fetchone()
    return bookAvailable

class BorrowBookRequest:
    def __init__(self, idBook, conn, cursor, user):
        self.idBook = idBook
        self.conn = conn
        self.cursor = cursor
        self.user = user
    def getIdBook(self):
        return self.idBook
    def getConn(self):
        return self.conn
    def getCursor(self):
        return self.cursor
    def getUser(self):
        return self.user

class BorrowBookRequestHandle:
    def execute(self, method):
        conn = method.getConn()
        cursor = method.getCursor()
        idBook = method.getIdBook()
        user = method.getUser()
        if getBookAvailability(idBook, cursor):
            cursor.execute('UPDATE books SET available = False WHERE id = %s;', [idBook])
            cursor.execute('INSERT INTO borrows (id_user, id_book, status_finished) VALUES (%s, %s, False);', [user[0], idBook])
            conn.commit()
            return True
        else: 
            cursor.execute('INSERT INTO waiting_list (id_user, id_book) VALUES (%s, %s)', [user[0], idBook])
            conn.commit()
            return False


class ReturnBookRequest:
    def __init__(self, idBook, conn, cursor, user):
        self.idBook = idBook
        self.conn = conn
        self.cursor = cursor
        self.user = user
    def getIdBook(self):
        return self.idBook
    def getConn(self):
        return self.conn
    def getCursor(self):
        return self.cursor
    def getUser(self):
        return self.user

class ReturnBookRequestHandle:
    def execute(self, method):
        conn = method.getConn()
        cursor = method.getCursor()
        idBook = method.getIdBook()
        user = method.getUser()

        cursor.execute('UPDATE books SET available = True WHERE id = %s;', [idBook])
        cursor.execute('UPDATE borrows SET status_finished = True WHERE id_user = %s AND id_book = %s', [user[0], idBook])
        conn.commit()

        return


class SignUpUserRequest:
    def __init__(self, conn, cursor, _name, _hashed_password, _email, _pricingPlan):
        self.conn = conn
        self.cursor = cursor
        self._name = _name
        self._hashed_password = _hashed_password
        self._email = _email
        self._pricingPlan = _pricingPlan
    def getConn(self):
        return self.conn
    def getName(self):
        return self._name
    def getPassword(self):
        return self._hashed_password
    def getEmail(self):
        return self._email
    def getPricingPlan(self):
        return self._pricingPlan
    def getCursor(self):
        return self.cursor

class SignUpUserRequestHandle:
    def execute(self, method):
        conn = method.getConn()
        cursor = method.getCursor()

        cursor.execute('INSERT INTO users (username, password, email, role, price_plan, approved_user) values (%s, %s, %s, \'user\', %s, False)',
                        [method.getName(), method.getPassword(), method.getEmail(), method.getPricingPlan()])
        conn.commit()

        return


class ValidateLogin:
    def __init__(self, cursor, _username):
        self.cursor = cursor
        self._username = _username
    def getUsername(self):
        return self._username
    def getCursor(self):
        return self.cursor

class ValidateLoginHandle:
    def execute(self, method):
        cursor = method.getCursor()
        username = method.getUsername()

        #get users with this username (should only be one)
        cursor.execute("SELECT * from users where username = %s", [username])
        users = cursor.fetchall()

        return users


class GetUserByIdRequest:
    def __init__(self, cursor, id):
        self.cursor = cursor
        self.id = id
    def getId(self):
        return self.id
    def getCursor(self):
        return self.cursor

class GetUserByIdRequestHandle:
    def execute(self, method):
        cursor = method.getCursor()

        cursor.execute('SELECT * FROM users WHERE id = %s', [method.getId()])
        user = cursor.fetchone()

        return user


class GetUsers:
    def __init__(self, cursor):
        self.cursor = cursor
    def getCursor(self):
        return self.cursor

class GetUsersHandle:
    def execute(self, method):
        cursor = method.getCursor()

        cursor.execute('SELECT id, username, email, price_plan FROM users')
        users = cursor.fetchall()

        return users

    
class GetInactiveUsers:
    def __init__(self, cursor):
        self.cursor = cursor
    def getCursor(self):
        return self.cursor

class GetInactiveUsersHandle:
    def execute(self, method):
        cursor = method.getCursor()

        cursor.execute('SELECT id, username, email, price_plan, approved_user FROM users WHERE approved_user = False')
        users = cursor.fetchall()

        return users


class ActivateUser:
    def __init__(self, conn, cursor, id):
        self.cursor = cursor
        self.conn = conn
        self.id = id
    def getCursor(self):
        return self.cursor
    def getConn(self):
        return self.conn
    def getId(self):
        return self.id

class ActivateUserHandle:
    def execute(self, method):
        cursor = method.getCursor()
        conn = method.getConn()

        cursor.execute('UPDATE users SET approved_user = True WHERE id = %s', [method.getId()])
        conn.commit()

        return


class GetUserBooks:
    def __init__(self, cursor, user):
        self.cursor = cursor
        self.user = user
    def getCursor(self):
        return self.cursor
    def getUser(self):
        return self.user

class GetUserBooksHandle:
    def execute(self, method):
        cursor = method.getCursor()
        user = method.getUser()

        cursor.execute('SELECT id_book FROM borrows WHERE id_user = %s AND status_finished = False', [user[0]])
        id_books = cursor.fetchall()

        books = list()
        for x in range(len(id_books)):
            cursor.execute('SELECT id, title, author, genre FROM books WHERE id = %s', [id_books[x]])
            book = cursor.fetchall()
            books.append(book[0])

        return books


class AddBook:
    def __init__(self, conn, cursor, details):
        self.cursor = cursor
        self.conn = conn
        self.details = details
    def getCursor(self):
        return self.cursor
    def getConn(self):
        return self.conn
    def getDetails(self):
        return self.details

class AddBookHandle:
    def execute(self, method):
        cursor = method.getCursor()
        conn = method.getConn()
        details = method.getDetails()

        cursor.execute("INSERT INTO books (title, author, genre, available) values (%s, %s, %s, True)", (details[0], details[1], details[2]))
        conn.commit()

        return


class GetAllBooks:
    def __init__(self, cursor):
        self.cursor = cursor
    def getCursor(self):
        return self.cursor

class GetAllBooksHandle:
    def execute(self, method):
        cursor = method.getCursor()

        cursor.execute('SELECT id, title, author, genre FROM books')
        books = cursor.fetchall()

        return books


class GetBook:
    def __init__(self, cursor, id):
        self.cursor = cursor
        self.id = id
    def getCursor(self):
        return self.cursor
    def getId(self):
        return self.id

class GetBookHandle:
    def execute(self, method):
        cursor = method.getCursor()

        cursor.execute('SELECT * FROM books WHERE id = %s', [method.getId()])
        book = cursor.fetchone()

        return books


class DeleteBook:
    def __init__(self, conn, cursor, id):
        self.cursor = cursor
        self.conn = conn
        self.id = id
    def getCursor(self):
        return self.cursor
    def getConn(self):
        return self.conn
    def getId(self):
        return self.id

class DeleteBookHandle:
    def execute(self, method):
        cursor = method.getCursor()
        conn = method.getConn()

        cursor.execute('DELETE FROM books WHERE id = %s', [method.getId()])
        conn.commit()

        return


dict_name_handle = {"BorrowBookRequest" : BorrowBookRequestHandle, 
                    "ReturnBookRequest" : ReturnBookRequestHandle,
                    "SignUpUserRequest" : SignUpUserRequestHandle,
                    "GetUserByIdRequest" : GetUserByIdRequestHandle,
                    "GetUsers" : GetUsersHandle,
                    "GetInactiveUsers" : GetInactiveUsersHandle,
                    "ActivateUser" : ActivateUserHandle,
                    "GetUserBooks" : GetUserBooksHandle,
                    "AddBook" : AddBookHandle,
                    "GetAllBooks" : GetAllBooksHandle,
                    "GetBook" : GetBookHandle,
                    "DeleteBook" : DeleteBookHandle,
                    "ValidateLogin" : ValidateLoginHandle}

class Mediator:
    def execute(self, method):
        return dict_name_handle[method.__class__.__name__]().execute(method)