# Flask Restful get and put sample 

from flask import Flask, request, abort
from flask.ext.restful import Resource, Api
from flask.ext.mongoengine import MongoEngine
from flask_redis import Redis
from flask.ext.bcrypt import Bcrypt
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'flask-test',
    'host': 'ds027741.mongolab.com',
    'port': 27741,
    'username': 'flask-admin',
    'password': '123123'
}

app.config['REDIS_URL'] = "redis://:123123@pub-redis-17784.us-east-1-2.1.ec2.garantiadata.com:17784/0"
app.config['SECRET_KEY'] = 'flask is cool'

db = MongoEngine(app)
redis_store = Redis(app)
bcrypt = Bcrypt(app)
api = Api(app)

class User(db.Document):
	# email = db.EmailField(unique=True)
    username = db.StringField(unique=True)
    password_hash = db.StringField()

    def hash_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps(self.username)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            username = s.loads(token)
        except SignatureExpired:
            return False    # valid token, but expired
        except BadSignature:
            return False    # invalid token
        if redis_store.get(username) == token:
            return True
        else:
            return False

class Todo(db.Document):
    text = db.StringField()

class UserAPI(Resource):
    def post(self):
        # email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        if username is None or password is None:
            abort(400)    # missing arguments
        user = User(username=username)
        user.hash_password(password)
        try:
            user.save()
        except:
            return {'status': 'error', 'message': 'username has already existed'}
        return ({'username': user.username}, 201)


class LoginAPI(Resource):
    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        if username is None or password is None:
            abort(400)
        user = User.objects(username=username)[0]
        if not user or not user.verify_password(password):
            abort(400)
        token = user.generate_auth_token(expiration=360000)
        redis_store.set(username, token)
        return {'token': token}
        

class TodoSimple(Resource):
    def get(self):
        token = request.form['token']
        if not User.verify_auth_token(token):
            abort(400)
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
api.add_resource(UserAPI, '/users')
api.add_resource(LoginAPI, '/login')


if __name__ == '__main__':
    app.run(debug=True)
