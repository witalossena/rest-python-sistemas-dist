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
    def get(self):  
        dict_args = request.args
        with open('templates/dynamic_page.html', 'w') as file:
            file.write(
                f'''
                    <!DOCTYPE html>
                        <html lang="pt-BR">

                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Api sist. Dist Python</title>
                                <link rel="preconnect" href="https://fonts.gstatic.com">
                                <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
                                <script>
                                    function startTime() {{
                                        var today = new Date();
                                        var h = today.getHours();
                                        var m = today.getMinutes();
                                        var s = today.getSeconds();
                                        m = checkTime(m);
                                        s = checkTime(s);
                                        document.getElementById('txt').innerHTML =
                                        h + ":" + m + ":" + s;
                                        var t = setTimeout(startTime, 500);
                                    }}
                                    function checkTime(i) {{
                                        if (i < 10) {{i = "0" + i}};  // add zero in front of numbers < 10
                                        return i;
                                    }}
                                </script>


                                <style type="text/css">
                                    html{{
                                        font-family: 'Open Sans', sans-serif;
                                    }}

                                    
                                </style>

                            </head>
                                <body onload="startTime()" style="background-color: { dict_args['fundo'] }"">
                                    <div>
                                       <h1 style="background-color: { dict_args['cor'] }">Hello, { dict_args['nome'] }!</h1>
                                        <p> Your request is coming from: {request.headers.get('User-Agent')}</p>
                                        <p> Your default language is: {request.accept_languages[0][0]}
                                        <p> Your ipaddress is: {request.remote_addr}</p>
                                    </div>
                                </body>
                        </html>
                '''
            )
        
        headers = {'Content-Type': 'text/html'}

        return make_response (render_template('dynamic_page.html'), 200, headers)

api.add_resource(TemplateRenderResourceInParams, '/api')



class TemplateRenderResourceInPost(Resource):
    def post(self):
        with open('templates/dynamic_page.html', 'w') as file:
            file.write(
                f'''
                    <!DOCTYPE html>
                        <html lang="pt-BR">

                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>POST REQUEST</title>
                                <link rel="preconnect" href="https://fonts.gstatic.com">
                                <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
                                <script>
                                    function startTime() {{
                                        var today = new Date();
                                        var h = today.getHours();
                                        var m = today.getMinutes();
                                        var s = today.getSeconds();
                                        m = checkTime(m);
                                        s = checkTime(s);
                                        document.getElementById('txt').innerHTML =
                                        h + ":" + m + ":" + s;
                                        var t = setTimeout(startTime, 500);
                                    }}
                                    function checkTime(i) {{
                                        if (i < 10) {{i = "0" + i}};  // add zero in front of numbers < 10
                                        return i;
                                    }}
                                </script>


                                <style type="text/css">
                                    html{{
                                        font-family: 'Open Sans', sans-serif;
                                    }}

                                    
                                </style>

                            </head>
                                <body style="background-color: { request.form['fundo'] }" onload="startTime()">
                                    <div>
                                        <h1 style="background-color: { request.form['cor'] }">Hello, { request.form['nome'].capitalize() }!</h1>
                                        <p> Your request is coming from: {request.headers.get('User-Agent')}</p>
                                        <p> {'Your Default Language is: ' + request.accept_languages if 'Postman' not in request.headers.get('User-Agent') else ''}</p>
                                        <p> Your ipaddress is: {request.remote_addr}</p>
                                    </div>
                                </body>
                        </html>
                '''
            )
        
        headers = {'Content-Type': 'text/html'}

        return make_response (render_template('dynamic_page.html'), 200, headers)

api.add_resource(TemplateRenderResourceInPost, '/api')




if __name__ == '__main__':
    app.run(debug=True)
