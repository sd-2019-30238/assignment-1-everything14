import datetime
from flask import json, Blueprint, request, render_template, redirect
from dbAccess import getConn


articles = Blueprint('articles', __name__, template_folder="static/templates")

@articles.route('/addArticleForm')
def addArticleForm():
	_user = session.get("user")
	if _user:
		return render_template('addArticle.html')
	else:
		return render_template('error.html', error = "Invalid User Credentials")

@articles.route('/<int:id>/editArticleForm')
def editArticleForm(id):
	_user = session.get("user")
	print("in edit form")
	if _user:
		return render_template('editArticle.html', id = id)
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
	return redirect('/blog')


@articles.route('/<int:id>/viewArticle', methods=['GET', 'POST'])
def viewArticle(id):
	print("in view article")
	conn = getConn()
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM articles WHERE id = %s', [id])
	article = cursor.fetchone()

	return render_template('viewArticle.html', article = article)


@articles.route('/<int:id>/editArticle',methods=['GET', 'POST'])
def editArticle(id):
	print("in editArticle")
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
			cursor.execute("UPDATE articles SET title = %s, text = %s WHERE id = %s ", (_title, _text, id))
			conn.commit()
		else:
			return render_template('error.html',error = 'Unauthorized Access')
	except Exception as e:
		print("in exception for addArticle")
		return render_template('error.html', error = str(e))

	finally:
		cursor.close()
		conn.close()
	return redirect('/blog')


@articles.route('/<int:id>/deleteArticle', methods=('DELETE',))
def deleteArticle(id):
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM articles WHERE id = %s', [id])
    conn.commit()

    return render_template('blog.html')

def insertTestData():
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO articles (title, author_id, text) values ('a', '1', 'a')")
    cursor.execute("INSERT INTO articles (title, author_id, text) values ('b', '1', 'b')")
    cursor.execute("INSERT INTO articles (title, author_id, text) values ('c', '1', 'c')")
    cursor.execute("INSERT INTO articles (title, author_id, text) values ('d', '1', 'd')")
    cursor.execute("INSERT INTO articles (title, author_id, text) values ('e', '1', 'e')")
    conn.commit()
