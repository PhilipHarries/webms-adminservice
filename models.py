from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):

    #password_hash = store this in the db somehow

    def __init__(self,e):
        self.email = e["email"]

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated():
        return True

    def is_active():
        return False

    def is_anonymous():
        return False

    def get_id(self):
        return self.email



# from example using pymongo:
#class User():
#
#    def __init__(self, username):
#        self.username = username
#        self.email = None
#
#    def is_authenticated(self):
#        return True
#
#    def is_active(self):
#        # but this should be something that can time out
#        return True
#
#    def is_anonymous(self):
#        return False
#
#    def get_id(self):
#        return self.username
#
#    @staticmethod
#    def validate_login(password_hash, password):
#        return check_password_hash(password_hash, password)

