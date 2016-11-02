"""
The flask application package.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, utils
from flaskext.sass import sass
from flask.ext.bower import Bower


app = Flask(__name__)
#app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(os.getcwd(), 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "WOWsEcReTkEYsdfghjklkjhgfds"

from .db_models import db, Project
db.app = app
db.init_app(app)

from .db_models import  user_datastore
security = Security(app, user_datastore)

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .db_models import User, UserAdmin, Role, RoleAdmin

admin = Admin(app, name='FlaskPortfolioPort', template_mode='bootstrap3')
admin.add_view(RoleAdmin(Project, db.session))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(RoleAdmin(Role, db.session))

sass(app, input_dir='static/scss', output_dir='static/css')
Bower(app)

from . import views

# Executes before the first request is processed to init database.
@app.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    #Create admin role and default user
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    encrypted_password = utils.encrypt_password('default_password')
    if not user_datastore.get_user('admin@localhost'):
        user_datastore.create_user(email='admin@localhost', password=encrypted_password)

    #nescessary before next step
    db.session.commit()

    user_datastore.add_role_to_user('admin@localhost', 'admin')
    db.session.commit()
