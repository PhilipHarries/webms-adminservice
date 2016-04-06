from flask import Flask, abort, send_file, render_template, make_response, jsonify, request
import os
from flask.ext.pymongo import PyMongo
from pymongo import MongoClient
import logging, requests, cStringIO,mimetypes
from logging.handlers import RotatingFileHandler
from .forms import AlbumRefreshForm, NewBlogForm, UpdateBlogForm, DeleteBlogForm, LoginForm
from .models import User
from flask_login import LoginManager, login_user
import flask.ext.login
from flask.ext.login import login_required

# should rewrite the abort handlers to return (helpful) html

debug = True

def debug_print(s):
    app.logger.debug(s)
    if(debug):
        print s

def error_print(e):
    app.logger.error(e)
    if(debug):
        print e

handler = RotatingFileHandler('./logs/adminservice.log',maxBytes=40960,backupCount=3)
handler.setLevel(logging.DEBUG)

# set the project root directory as the static folder
app = Flask(__name__, static_url_path='/static')


app.config['DEBUG'] = True
try:
    app.config['SECRET_KEY'] = os.environ['ADMIN_SECRET']
except KeyError as KE:
    error_print("Bailing out: environment variable missing: {}".format(KE))
    exit(1)

app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = "login"
login_manager.login_message = "Please login"


# need to load from email id
@login_manager.user_loader
def load_user(email_id):
    user = mongo.db.user.find_one({"email": email_id})
    if not user:
        return None
    return User(user)



# connect to mongo with defaults
mongo = PyMongo(app)

blog_service_url = "http://localhost:5434/blog/api/v1.0"
flickr_service_url = "http://localhost:5433/flickr/api/v1.0"
flickr_userid = "Philip_UK"

@app.errorhandler(404)
def not_found(error):
    debug_print(error)
    return make_response(jsonify({'error': '404: not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    debug_print(error)
    return make_response(jsonify({'error': '400: bad request'}), 400)

@app.errorhandler(401)
def bad_request(error):
    debug_print(error)
    #return redirect(url_for('login'))
    return make_response(jsonify({'error': '401: not authorised'}), 401)

@app.errorhandler(409)
def bad_request(error):
    debug_print(error)
    return make_response(jsonify({'error': '409: duplicate resource id'}), 409)

@app.errorhandler(500)
def internal_server_error(error):
    debug_print(error)
    return make_response(jsonify({'error': '500: internal server error'}), 500)

@app.errorhandler(501)
def not_implemented(error):
    debug_print(error)
    return make_response(jsonify({'error': '501: HTTP request not understood in this context'}), 501)

@app.errorhandler(502)
def bad_gateway(error):
    debug_print(error)
    return make_response(jsonify({'error': '502: server received an invalid response from an upstream server'}), 502)

@app.errorhandler(503)
def service_unavailable(error):
    debug_print(error)
    return make_response(jsonify({'error': '503: service unavailable - try back later'}), 503)

@app.errorhandler(504)
def gateway_timeout(error):
    debug_print(error)
    return make_response(jsonify({'error': '504: upstream timeout - the server stopped waiting for a response from upstream'}), 504)


#@app.route('/', methods=['GET'])
@app.route('/')
@login_required
def home():
    return render_template('index.html')

def next_is_valid(url):
    return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Log in and validate the user
        # user should be an instance of the User class
        print("Finding user where email is {}...".format(form.email.data))
        user = mongo.db.user.find_one({"email": form.email.data})
        print("Found {}".format(user))
        print(" user password: {}".format(user["password"]))
        print(" user email: {}".format(user["email"]))
        #if user and User.verify_password(user['password'], form.password.data):
        if user and user['password'] == form.password.data:
            user_obj = User(user)
            debug_print(user)
            debug_print(user_obj)
            login_user(user_obj)
            flask.flash("logged in successfully", category='success')
            next = flask.request.args.get('next')
            if not next_is_valid(next):
                return flask.abort(401)
            return flask.redirect(next or flask.url_for('login'))
    return render_template('login.html', 
                           title='Sign In',
                           form=form)



@app.route('/blog_admin', methods=['GET','POST'])
@login_required
def blog_admin():
    message=None
    new_blog_form = NewBlogForm()
    update_blog_form = UpdateBlogForm()
    delete_blog_form = DeleteBlogForm()
    if request.method == 'POST':
        debug_print("Got a post")
        if request.form['submit'] == "Submit":
            if new_blog_form.validate_on_submit():
                r = requests.post("{}/blogs".format(blog_service_url), json={
                    "id": request.form["id"],
                    "title": request.form["title"],
                    "content": request.form["content"],
                    "description": request.form["description"],
                    "tags": request.form["tags"],
                    "author": request.form["author"]
                    })
                if r.ok:
                    message="You've only gone and submitted a new blog!"
                else:
                    message="Something went wrong submitting your blog, sorry!"
        elif request.form['submit'] == "Update":
            debug_print("Got an update")
            if update_blog_form.validate_on_submit():
                debug_print("{}/blog/{}".format(blog_service_url,request.form["id"]))
                payload = {
                    "title": request.form["title"],
                    "content": request.form["content"],
                    "description": request.form["description"],
                    "tags": request.form["tags"],
                    "author": request.form["author"]
                }
                r = requests.put("{}/blog/{}".format(blog_service_url,request.form["id"]), json=payload)
                if r.ok:
                    message="You've only gone and updated an existing blog!"
                else:
                    debug_print(r.status_code)
                    debug_print(r.text)
                    debug_print(r.url)
                    debug_print(payload)
                    message="We have failed to update the blog. :("
        elif request.form['submit'] == "Delete Post":
            if delete_blog_form.validate_on_submit():
                try:
                    r = requests.delete("{}/blog/{}".format(blog_service_url,request.form["id"]))
                except Exception as e:
                    debug_print(e)
                    message="Something unexpected has been submitted\n{}".format(e)
                message="You've only gone and deleted an existing blog!\n {}".format(request.form["id"])
        else:
            message="Something unexpected has been submitted"
    r = requests.get("{}/blogs".format(blog_service_url))
    blogs=r.json()["blogs"]
    blogs.reverse()
    return render_template('blog_admin.html',
                            blogs=blogs,
                            new_blog_form=new_blog_form,
                            update_blog_form=update_blog_form,
                            delete_blog_form=delete_blog_form,
                            message=message)




@app.route('/album_admin', methods=['GET','POST'])
@login_required
def album_admin():
    albums = []
    album_refresh_form = AlbumRefreshForm()
    message=""
    if album_refresh_form.validate_on_submit():
        r = requests.post("{}/refresh_albums".format(flickr_service_url), json={"album_ids": [ album_refresh_form.album_id.data ], "owner_id": "Philip_UK" })
        if r.ok:
            albums_request = requests.get("{}/albums/{}".format(flickr_service_url,flickr_userid))
            message="Updated {}".format(album_refresh_form.album_id.data)
            debug_print(r.text)
    debug_print("Contacting {}/albums/{}".format(flickr_service_url,flickr_userid))
    albums_request = requests.get("{}/albums/{}".format(flickr_service_url,flickr_userid))
    if albums_request.ok:
        for album in albums_request.json()["albums"]:
            if album["id"] != "cacheInfo":
                albums.append(album)
    else:
        abort(502)
    return render_template('album_admin.html',
                        albums=albums,
                        message=message,
                        album_refresh_form=album_refresh_form)

@app.route('/album/<string:album_id>', methods=['GET'])
@login_required
def get_album(album_id):
    debug_print("Contacting {}/album/{}/{}".format(flickr_service_url,flickr_userid,album_id))
    album_request = requests.get("{}/album/{}/{}".format(flickr_service_url,flickr_userid,album_id))
    if album_request.status_code == 404:
        abort(404)
    elif album_request.status_code == 500:
        abort(500)
    debug_print(album_request.json())
    album=album_request.json()["album"]
    return render_template('album.html', album=album)

@app.route('/image/flickr/<string:user_id>/<string:album_id>/<string:image_id>/<string:image_type>', methods=['GET'])
def get_image(user_id,album_id,image_id,image_type):
    debug_print("Contacting {}/{}/{}/{}/{}".format(flickr_service_url,image_type,flickr_userid,album_id,image_id))
    image_request = requests.get("{}/{}/{}/{}/{}".format(flickr_service_url,image_type,flickr_userid,album_id,image_id))
    if image_request.status_code == 404:
        abort(404)
    elif image_request.status_code == 500:
        abort(500)
    img_io = cStringIO.StringIO()
    img_io.write(image_request.content)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')



if __name__ == '__main__':
    app.run(debug=True)


