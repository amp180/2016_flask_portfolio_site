from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, utils
from flask_admin.contrib import sqla
from wtforms.fields import PasswordField
from flask_login import current_user
db = SQLAlchemy()


class Project(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, db.Sequence('id_seq', start=1, increment=1), primary_key=True)
    name = db.Column(db.String(50))
    img_url = db.Column(db.Text())
    publish_date = db.Column(db.Date())
    html = db.Column(db.Text())

    def __init__(self, name="", img_url="", publish_date="", html=""):
        self.name = name
        self.img_url = img_url
        self.publish_date = publish_date
        self.html = html

    def is_accessible(self):
        return current_user.has_role('admin')

    def __repr__(self):
        return "<Project('%s', '%s', '%s')>" % (self.name, self.img_url, self.publish_date)

#Following is taken from  https://github.com/sasaporta/flask-security-admin-example/blob/master
#Basic Flask-Security database roles.

#User-Role pairs.
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


# Role class
class Role(db.Model, RoleMixin):

    # Our Role has three fields, ID, name and description
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


# User class
class User(db.Model, UserMixin):

    # Our User has six fields: ID, email, password, active, confirmed_at and roles. The roles field represents a
    # many-to-many relationship using the roles_users table. Each user may have no role, one role, or multiple roles.
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __repr__(self):
         return "({0}: {1})".format(self.id, self.email)

# Initialize the SQLAlchemy data store and Flask-Security.
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

# Customized User model for SQL-Admin
class UserAdmin(RoleAdmin):

    # Don't display the password on the list of Users
    column_exclude_list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)


