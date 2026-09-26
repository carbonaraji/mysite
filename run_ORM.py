# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
# .venv/Scripts/activate.ps1

 # 1. В папке проекта site2 python -m venv .venv .venv\Scripts\Activate.ps1 # 2. VS Code: Ctrl+Shift+P «Python: Выбор интерпретатора» → .venv\Scripts\python.exe 

from flask import Flask, render_template, request, redirect, url_for
#render_template - функция, которая показывает страницы из папки темплейтс
#request - переменная в которой хранятся методы пост или гет и в которой хранятся данные, которые мы передаем из сайта
#redirect - функция, которая перемещает на другую страницу
#url_for - функция, которая запускает другие функции по их названию
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__) #создаем объект приложения на основе класса фласк

#конфигурация нашего приложения(сайта)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "121987varya"

db=SQLAlchemy(app) #создаем базу данных

login_manager=LoginManager(app) #обЪект login_manager авторизовывает нас 
login_manager.login_view="login" #указываем, что авторизовывать будет функция с названием логин



class Blog(db.Model): #класс блог в пайтоне соответствует таблице блогс в базе данных
    __tablename__="blogs" #даем название таблицы
    id=db.Column(db.Integer,primary_key=True) #колонка с целыми числами
    title=db.Column(db.String, nullable=False) #колонка с текстом
    img=db.Column(db.String)
    content=db.Column(db.String)
    likes=db.relationship("Like",backref="idea",lazy="dynamic")



class User(UserMixin, db.Model):   #класс юзер соотетствует таблице юзерс в базе данных
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String, nullable=False, unique=True)
    password=db.Column(db.String, nullable=False)
    avatar=db.Column(db.String)
    email=db.Column(db.String)
    likes=db.relationship("Like",backref="user",lazy="dynamic")



class Like(db.Model):
    __tablename__="likes"
    id=db.Column(db.Integer,primary_key=True)
    idea_id=db.Column(db.Integer, db.ForeignKey("blogs.id"))
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"))


@app.route("/")
def index():
    posts=Blog.query.all() #класс блог-это таблица блогс с помощью квери делаем запрос к этой таблице, с помощью олл забираем все и ложим в переменную постс
    name = "Вари"
    posts_data=[] #список в который мы кладем идеи, их количество лайков и поставлен лайк или нет
    for post in posts:
        likes_count=post.likes.count()
        is_liked=False
        if current_user.is_authenticated:
            is_liked=post.likes.filter_by(user_id=current_user.id).first() is not None
        posts_data.append({
            "post": post,"likes_count": likes_count, "is_liked": is_liked
        })
    return render_template("index.html",name=name, res=posts_data)


@app.route("/idea/<idea_id>")
def idea(idea_id):
    post=Blog.query.get(idea_id)
    return render_template("idea.html",my_idea=post)


@app.route("/add_idea",methods=["POST","GET"]) #метод пост отправляет данные с сайта в наш код, гет показывает страницу
def add_idea():
    if request.method=="POST": #если мы отправляем данные из сайта
        title=request.form["title"] #в переменную тайтл ложим данные из прямоугольника заголовок идеи, который мы заполняем на сайте
        img=request.form["img"] #в переменную имджи ложим данные из прямоугольника картинка, который мы заполняем на сайте
        content=request.form["content"] #в переменную контент ложим данные из прямоугольника описание идеи, который мы заполняем на сайте
        new_post=Blog(title=title,img=img,content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("index")) #редирект перемещает нас на другую страницу(на главную)
    return render_template("add_idea.html")

####----------------------------------------------

@app.route("/del_idea/<idea_id>",methods=["POST"])
def del_idea(idea_id):
    post = Blog.query.get(idea_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))

####-----------------------------------------------


@app.route("/edit_idea/<idea_id>",methods=["POST", "GET"])
def edit_idea(idea_id):
    post=Blog.query.get(idea_id)
    if request.method=="POST": #если мы отправляем данные из сайта
        post.title=request.form["title"] #в переменную тайтл ложим данные из прямоугольника заголовок идеи, который мы заполняем на сайте
        post.img=request.form["img"] #в переменную имджи ложим данные из прямоугольника картинка, который мы заполняем на сайте
        post.content=request.form["content"] #в переменную контент ложим данные из прямоугольника описание идеи, который мы заполняем на сайте
        db.session.commit()  #сохранение изменений
        return redirect(url_for("index"))  #перемещение на главную страницу
    return render_template("edit_idea.html", post=post)  #все остальное время показываем эту страницу  


#USER


@app.route("/del_user/<user_id>",methods=["POST"]) #app route-адрес по которому буудет работать функция
def del_user(user_id):
    user = User.query.get(user_id)  #ищем пользователя по айди
    db.session.delete(user)  #удаляем пользователя
    db.session.commit()  #подтверждаем удаление
    return redirect(url_for("index")) #перемещаемся на главную страницу


@app.route("/edit_user/<user_id>",methods=["POST", "GET"])  #app route-адрес по которому буудет работать функция
def edit_user(user_id):
    user=User.query.get(user_id) #ищем пользователя по айди
    if request.method=="POST": #если мы отправляем данные из сайта
        user.email=request.form["email"] #берем данные в форме из поля, где имя=почта
        user.avatar=request.form["avatar"] #берем данные в форме из поля, где имя=аватар
        user.name=request.form["name"] #берем данные в форме из поля, где имя=имя
        db.session.commit()  #сохранение изменений
        return redirect(url_for("index"))  #перемещение на главную страницу
    return render_template("edit_user.html", user=user)  #все остальное время показываем эту страницу


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method=="POST":
        name=request.form["name"]
        password=request.form["password"]
        hash=generate_password_hash(password)
        avatar=request.form["avatar"]
        email=request.form["email"]
        new_user=User(name=name, password=hash, avatar=avatar, email=email) #создание нового пользователя
        db.session.add(new_user) #добавление нового пользователя
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("register.html")


@login_manager.user_loader #функция, которая загружает пользователя из юзер в авторизованного пользователя(current_user)
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/users")
def users():
    all_users=User.query.all()
    return render_template("users.html", all_users=all_users)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method=="POST":
        name=request.form["name"]
        password=request.form["password"]     
        user=User.query.filter_by(name=name).first() #получаем пользователя по имени
        if user and check_password_hash(user.password, password): #если пользователь найден и пароли совпадают
            login_user(user) #происходит авторизация пользователя
            return redirect(url_for("index"))
    return render_template("login.html")


# logout-выход из авторизованного пользователя
@app.route("/logout")
@login_required #показывает, что функция доступна только авторизованным пользователям
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile/<name>")
@login_required
def profile(name):
    return render_template("profile.html",name=name)


#LIKE

@app.route("/like/<idea_id>",methods=["POST"])
def like(idea_id):
    current_idea=Blog.query.get(idea_id) #получение идеи из базы данных по айди
    current_like=Like.query.filter_by(idea_id=current_idea.id,user_id=current_user.id).first()
    if current_like:
        db.session.delete(current_like)
    else:
        new_like=Like(idea_id=current_idea.id, user_id=current_user.id) #создаем новый лайк 
        db.session.add(new_like) #добавляем его в таблицу
    db.session.commit()
    return redirect(url_for("index"))


if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)