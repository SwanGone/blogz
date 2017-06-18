from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:matahari@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    blogbody = db.Column(db.String(1600))
    completed = db.Column(db.Boolean)

    def __init__(self, name):
        self.name = name
        self.blogbody = ""
        self.completed = False


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return redirect('/blog')

    task_name = request.form['task']
    new_body = request.form['body']
    if not new_body and not task_name:
        return render_template('newpost.html', error="Come on. Enter something. I won't judge you!")
    elif not task_name:
        return render_template('newpost.html', error="Please enter a title for your blog post")
    elif not new_body:
        return render_template('newpost.html', error="Your post has to say something!")
    new_task = Task(task_name)
    new_task.blogbody = new_body
    db.session.add(new_task)
    db.session.commit()
    task_for_grab = Task.query.filter_by(name=task_name).first()

    return redirect('/post?task-id=' + str(task_for_grab.id))


@app.route('/blog')
def blog():
    tasks = Task.query.all()
    return render_template('blog.html', title="BLOGGO", tasks=tasks)

@app.route('/newpost')
def newpost():
    return render_template('newpost.html')

@app.route('/post')
def post():
    task_id = int(request.args.get('task-id'))
    task = Task.query.filter_by(id=task_id).first()
    return render_template('post.html', task=task)

if __name__ == '__main__':
    app.run()