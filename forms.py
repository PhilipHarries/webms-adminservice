from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Required, Email, Length

class LoginForm(Form):
    csrf_secret = b'abcde'
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Log in')

class AlbumRefreshForm(Form):
    csrf_secret = b'fghij'
    album_id = StringField()
    owner_id = StringField()
    refresh = SubmitField('Refresh Cache')

class NewBlogForm(Form):
    csrf_secret = b'klmno'
    title = StringField()
    description = StringField()
    author = StringField()
    tags = StringField()
    content = StringField()
    submit = SubmitField('Submit')
    

class UpdateBlogForm(Form):
    csrf_secret = b'pqrst'
    title = StringField()
    description = StringField()
    author = StringField()
    tags = StringField()
    content = StringField()
    submit = SubmitField('Update')

    def validate_on_submit(self):
        print "Validated"
        return True

class DeleteBlogForm(Form):
    csrf_secret = b'uvwxy'
    id = StringField()
    submit = SubmitField('Delete Post')

