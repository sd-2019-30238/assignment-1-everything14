import datetime
from flask import json, Blueprint, request
from dbAccess import getConn


messages = Blueprint('messages', __name__, template_folder="static/templates")

@messages.route('/leaveMessage', methods=['POST'])
def leaveMessage():
	conn = getConn()
	cursor = conn.cursor()

	try:
		_subject = request.form['inputSubject']
		_email = request.form['inputEmail']
		_text = request.form['inputText']

		if _subject and _email and _text:
			print("Email:", _email, "\n", "Subject:", _subject, "\n", "Text:", _text)

			cursor.execute('INSERT INTO messages (subject, email, text, date) values (%s, %s, %s, %s)', [_subject, _email, _text, datetime.datetime.now()])
			conn.commit()
		else:
			print('fields not submitted')
			return 'Enter the required fields'

	except Exception as ex:
		print('got an exception: ', ex)
		return json.dumps({'error':str(ex)})

	finally:
		cursor.close()
		conn.close()
	return "OK"

@messages.route('/getAllMessages',methods=['GET'])
def getAllMessages():
    conn = getConn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, subject, email, date, text FROM messages')
        messages = cursor.fetchall()
        messages_list = [{"Id": message[0], "Subject": message[1], "Email": message[2], "Date": message[3], "Text": message[4]} for message in messages]

        print(messages_list)

        return json.dumps(messages_list)

    except Exception as e:
        return render_template('error.html', error = str(e))

    finally:
        cursor.close()
        conn.close()
