import datetime

from flask import Flask, render_template, request, url_for, redirect, session, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testblogdate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'destertopinworld'


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(128), nullable=False)
    post_about = db.Column(db.String(128), nullable=False)
    post_text = db.Column(db.Text(), nullable=False)
    post_author = db.Column(db.Text(25), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    post_last_edit_time = db.Column(db.DateTime)

    def __init__(self, post_title, post_about, post_text, post_author, post_last_edit_time):
        self.post_title = post_title
        self.post_about = post_about
        self.post_text = post_text
        self.post_author = post_author
        self.post_last_edit_time = post_last_edit_time

    def __repr__(self):
        return '<Posts %r>' % self.id


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.Text(), nullable=False)
    date_reg = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return '<Users %r>' % self.id


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user:
        return render_template('index.html', login=True)
    else:
        return render_template('index.html', login=False)


#Відображення постів
@app.route('/allPosts/<int:id_list>', methods=['GET', 'POST'])
def main_page(id_list):
    all_posts = Posts.query.order_by(Posts.created_date.desc()).all()
    id_size = id_list*10-10
    all_posts = all_posts[id_size:]
    all_posts = all_posts[:10]
    len_posts = len(all_posts)
    if g.user:
        return render_template('all_posts_page.html', all_posts=all_posts, len_posts=len_posts, id_list=id_list,
                               access=True, login=True)
    return render_template('all_posts_page.html', all_posts=all_posts, len_posts=len_posts, id_list=id_list,
                           access=False, login=False)


#Відображення одного поста
@app.route('/allPosts/post/<int:id>', methods=['GET', 'POST'])
def open_post(id):
    post = Posts.query.get_or_404(id)
    if g.user:
        return render_template('one_post_page.html', post=post, login=True)
    return render_template('one_post_page.html', post=post, login=False)


#Видалення поста
@app.route('/allPosts/post/<int:id>/delete')
def delete_post(id):
    if g.user:
        post = Posts.query.get_or_404(id)
        try:
            db.session.delete(post)
            db.session.commit()
            return redirect('/allPosts/1')
        except:
            return "Видалити пост не вийшло"
    return redirect(url_for('index'))


#Редагування поста
@app.route('/allPosts/post/<int:id>/edit', methods=['POST','GET'])
def edit_post(id):
    if g.user:
        post = Posts.query.get_or_404(id)
        if request.method == 'POST':
            post.post_title = request.form['post_title']
            post.post_text = request.form['post_text']
            post.post_about = request.form['post_about']
            post.post_last_edit_time = datetime.datetime.now()
            try:
                db.session.commit()
                return redirect('/allPosts/1')
            except:
                return "Не вийшло редагувати пост"
        else:
            if g.user:
                return render_template("edit_post_page.html", post=post, login=True)
            return render_template("edit_post_page.html", post=post, login=False)
    return redirect(url_for('index'))


#Вхід користувача
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ''
    if not g.user:
        if request.method == 'POST':
            session.pop('user', None)
            username = request.form['username']
            acc = Users.query.filter_by(username=username).first()
            if acc is None:
                error_msg = 'Такий акаунт не існує'
                return render_template('login_page.html', error_msg=error_msg, login=False)
            else:
                if request.form['password'] == acc.password:
                    session['user'] = acc.username
                    return redirect(url_for('index'))
                else:
                    error_msg = 'Логін або пароль не правильний'
                    return redirect(url_for('login', error_msg=error_msg, login=False))
        return render_template('login_page.html', error_msg=error_msg, login=False)
    return redirect(url_for('index'))


#Реєстрація
@app.route('/register', methods=['POST', 'GET'])
def register():
    if g.user:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            check_user = Users.query.filter_by(username=username).first()
            if check_user is None:
                acc = Users(username, password, email)
                try:
                    db.session.add(acc)
                    db.session.commit()
                    return redirect(url_for('index'))
                except:
                    return 'Не вийшло створити акаунт'
            else:
                return render_template('register_page.html', create=True, login=False)
        return render_template('register_page.html', create=False, login=False)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


#drop session
@app.route('/logout')
def logout():
    if g.user:
        session.pop('user', None)
        return redirect(url_for('index'))
    return redirect(url_for('index'))
    

#Створення постів
@app.route('/create', methods=['POST', 'GET'])
def create_post():
    if request.method == "POST":
        post_title = request.form['post_title']
        post_text = request.form['post_text']
        post_about = request.form['post_about']
        post_author = request.form['post_author']
        post = Posts(post_title=post_title, post_about=post_about, post_text=post_text, post_author=post_author, post_last_edit_time=datetime.datetime.now())
        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/allPosts/1')
        except:
            return "Створити пост не вийшло."
    else:
        if g.user:
            return render_template('create_post_page.html', login=True)
        return render_template('create_post_page.html', login=False)


if __name__ == '__main__':
    app.run()
