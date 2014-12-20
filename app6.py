# Flask Restful get and put sample 

from flask import Flask, request
from flask.ext.restful import Resource, Api
from flask.ext.mongoengine import MongoEngine
from flask.ext.bcrypt import Bcrypt


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask-test',
    'host': 'ds027741.mongolab.com',
    'port': 27741,
    'username': 'flask-admin',
    'password': '123123'
}
db = MongoEngine(app)
api = Api(app)

class User(db.Document):
	email = db.EmailField(unique=True)
    name = db.StringField(unique=True)
    password = db.StringField()

class TodoSimple(Resource):
    def get(self):
        todos =  Todo.objects.all()
        result = []
        for todo in todos:
        	result.append({'todo': todo.text})
        return result


    def put(self):
        todo = Todo(text=request.form['data'])
        todo.save()
        return {'status': 'success'}

api.add_resource(TodoSimple, '/todos')

if __name__ == '__main__':
    app.run(debug=True)
