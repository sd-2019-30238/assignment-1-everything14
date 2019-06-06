import datetime
from flask import json, Blueprint, request
from dbAccess import getConn


articles = Blueprint('articles', __name__, template_folder="static/templates")

@articles.route('/addArticleForm')
def addArticleForm():
	_user = session.get("user")
	if _user:
		return render_template('addArticle.html')
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@articles.route('/getAllArticles', methods=['GET'])
def getAllArticles():
	conn = getConn()
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


@articles.route('/addArticle',methods=['GET', 'POST'])
def addArticle():
	print("in addArticle")
	try:
		_user = session.get('user')
		if _user:
			print(_user)
			_title = request.form['inputTitle']

			_text = request.form['inputText']
			conn = getConn()
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


@articles.route('/<int:id>/viewArticle', methods=('POST',))
def viewArticle(id):
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE id = %s', [id])
    book = cursor.fetchone()
    
    return render_template('viewArticle.html')


@articles.route('/<int:id>/deleteArticle', methods=('POST',))
def deleteArticle(id):
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM articles WHERE id = %s', [id])
    conn.commit()

    return redirect('/userHome')
