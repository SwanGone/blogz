from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:matahari@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'godisasadistandheknowsit'


class BlogPost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    blogbody = db.Column(db.String(1600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.blogbody = ""
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('BlogPost', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/logout", methods=['POST'])
def logout():
    if 'username' not in session:
        return redirect("/login")
    else:
        del session['username']
        return redirect("/login")


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'logout', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('You are not logged in', 'error')
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged In', 'success')
            return redirect('/newpost')
        elif not user:
            flash('Username does not exist in database', 'error')
            return redirect('/login')
        elif user and user.password != password:
            flash('Incorrect password', 'error')
            return redirect('/login')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        sign_up_err_check = 0

        if not username:
            sign_up_err_check = 1
            flash('Please enter a username', 'error')
        elif re.search('\s', username) or not re.search('\S{4,20}', username):
            sign_up_err_check = 1
            flash('Please enter a valid username (Must be between 3 and 20 characters with no spaces)', 'error')

        if not password:
            sign_up_err_check = 1
            flash('Please enter a password', 'error')
        elif re.search('\s', password) or not re.search('\S{4,20}', password):
            sign_up_err_check = 1
            flash('Please enter a valid password (Must be between 3 and 20 characters with no spaces', 'error')

        if not verify:
            sign_up_err_check = 1
            flash('Please verify your password', 'error')
        elif verify != password:
            sign_up_err_check = 1
            flash('Your passwords do not match', 'error')
        
        if not sign_up_err_check:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = new_user.username
                flash('Signed up! Signed in!', 'success')
                return redirect('/newpost')

            else:
                flash('This user already exists', 'error')
                return render_template('signup.html')

    return render_template('signup.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    names = User.query.all()
    return render_template('index.html', title="Authors", names=names)


@app.route('/blog')
def blog():
    user_id = request.args.get('user-id')
    authors = User.query.all()
    if not user_id:
        tasks = BlogPost.query.all()
        return render_template('blog.html', title="BLOGZ!", tasks=tasks, authors=authors)
    else:
        tasks = BlogPost.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', title="BLOGZ!", tasks=tasks, authors=authors)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        post_name = request.form['blog_name']
        new_body = request.form['body']
        if not new_body and not post_name:
            flash("Come on. Enter something. I won't judge you!", 'error')
            return render_template('newpost.html')
        elif not post_name:
            flash("Please enter a title for your blog post", 'error')
            return render_template('newpost.html')
        elif not new_body:
            flash("Your post has to say something!", 'error')
            return render_template('newpost.html')
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = BlogPost(post_name, owner)
        new_blog.blogbody = new_body
        db.session.add(new_blog)
        db.session.commit()
        task_for_grab = BlogPost.query.filter_by(name=post_name).first()

        return redirect('/post?task-id=' + str(task_for_grab.id))

    else:    
        return render_template('newpost.html')

@app.route('/post')
def post():
    task_id = int(request.args.get('task-id'))
    task = BlogPost.query.filter_by(id=task_id).first()
    return render_template('post.html', task=task)

if __name__ == '__main__':
    app.run()