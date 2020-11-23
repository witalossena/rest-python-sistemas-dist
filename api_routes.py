from flask import Flask, request, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(255))

    def __repr__(self):
        return '<User %s>' % self.name


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email")
        model = User


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserListResource(Resource):
    # method GET  url: http://127.0.0.1:5000/users
    def get(self):
        users = User.query.all()
        if users == []:
            return "0 usuarios cadastrados"
        return users_schema.dump(users)

    # method POST  url: http://127.0.0.1:5000/users
    def post(self):
        name = request.form['name']
        email = request.form['email']
        new_user = User(
            name=name,
            email=email
        )
        db.session.add(new_user)
        db.session.commit()
        return user_schema.dump(new_user)


api.add_resource(UserListResource, '/users')


class UserResource(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        return user_schema.dump(user)

    def patch(self, id):
        user = User.query.get_or_404(id)
        if 'name' in request.form:
            user.name = request.form['name']
        if 'email' in request.form:
            user.email = request.form['email']
        db.session.commit()
        return user_schema.dump(user)

    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204


api.add_resource(UserResource, '/users/<int:id>')


class TemplateRenderResourceInParams(Resource):
    def get(self,name="witalo", bgColor="red" ):   
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html', name=name, bgColor=bgColor), 200, headers)

api.add_resource(TemplateRenderResourceInParams, '/home/<name>/<bgColor>')



class TemplateRenderResourceInPost(Resource):
    def post(self):
        name=request.form['nome']
        bgColor=request.form['cor']
        bodyColor=request.form['fundo']
        headers = {'Content-Type': 'text/html'}
        return make_response( render_template('index.html', name=name, bgColor=bgColor, bodyColor=bodyColor), 200, headers)     

api.add_resource(TemplateRenderResourceInPost, '/home')




if __name__ == '__main__':
    app.run(debug=True)
