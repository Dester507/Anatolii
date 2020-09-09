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


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html')


#Відображення постів
@app.route('/allPosts/<int:id_list>', methods=['GET', 'POST'])
def main_page(id_list):
    all_posts = Posts.query.order_by(Posts.created_date.desc()).all()
    id_size = id_list*10-10
    all_posts = all_posts[id_size:]
    all_posts = all_posts[:10]
    len_posts = len(all_posts)
    return render_template('all_posts_page.html', all_posts=all_posts, len_posts=len_posts, id_list=id_list)


#Відображення одного поста
@app.route('/allPosts/post/<int:id>', methods=['GET', 'POST'])
def open_post(id):
    #Перевірка на адміна

    if g.user:
        #Доступ до видалення і редагування
        post = Posts.query.get_or_404(id)
        return render_template('one_post_page.html', post=post, access=True)
    post = Posts.query.get_or_404(id)
    return render_template('one_post_page.html', post=post, access=False)
    #Без доступу до видалення і редагування



#Видалення поста
@app.route('/allPosts/post/<int:id>/delete')
def delete_post(id):
    post = Posts.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        return redirect('/allPosts/1')
    except:
        return "Видалити пост не вийшло"


#Редагування поста
@app.route('/allPosts/post/<int:id>/edit', methods=['POST','GET'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    if request.method == 'POST':
        post.post_title = request.form['post_title']
        post.post_text = request.form['post_text']
        post.post_about = request.form['post_about']
        post.post_last_edit_time = datetime.datetime.now()
        try:
            db.session.commit()
            return redirect('/allPosts/1')
        except :
            return "Не вийшло редагувати пост"
    else:
        return render_template("edit_post_page.html", post=post)


#Вхід користувача
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)

        if request.form['password'] == 'password':
            session['user'] = request.form['username']
        return redirect(url_for('/'))
    return render_template('login_page.html')


@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']


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
         return render_template('create_post_page.html')


if __name__ == '__main__':
    app.run()
