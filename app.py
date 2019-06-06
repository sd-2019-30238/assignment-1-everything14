from flask import Flask
from messages import messages
from articles import articles, insertTestData
from users import users
from menu import menu
from send import send


#initialize the flask and SQL Objects
app = Flask(__name__, template_folder="static/templates")
app.register_blueprint(messages)
app.register_blueprint(articles)
app.register_blueprint(users)
app.register_blueprint(menu)
app.register_blueprint(send)

#initialize secret key
app.secret_key='This is my secret key'

if __name__ == "__main__":
    #insertTestData()
    app.run()
